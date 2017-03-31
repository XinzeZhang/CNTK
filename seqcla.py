# Copyright (c) Microsoft. All rights reserved.

# Licensed under the MIT license. See LICENSE.md file in the project root
# for full license information.
# ==============================================================================

import sys
import os
from cntk import Trainer, Axis #, text_format_minibatch_source, StreamConfiguration
from cntk.io import MinibatchSource, CTFDeserializer, StreamDef, StreamDefs, INFINITELY_REPEAT
from cntk.device import cpu, try_set_default_device
from cntk.learners import sgd, learning_rate_schedule, UnitType
from cntk.ops import input, sequence, relu
from cntk.losses import cross_entropy_with_softmax
from cntk.metrics import classification_error
from cntk.logging import *
from cntk.layers import *



# Creates the reader
def create_reader(path, is_training, input_dim, label_dim):
    return MinibatchSource(CTFDeserializer(path, StreamDefs(
        features = StreamDef(field='x', shape=input_dim,   is_sparse=True),
        labels   = StreamDef(field='y', shape=label_dim,   is_sparse=False)
    )), randomize=is_training, max_sweeps = INFINITELY_REPEAT if is_training else 1)

# Defines the LSTM model for classifying sequences
def create_model(feature, num_output_classes, embedding_dim, LSTM_dim, cell_dim):
    return Sequential([
        Embedding(embedding_dim),
        Fold(RNNUnit(cell_dim, activation=relu)),
        Dense(num_output_classes)
    ])(feature)

# Creates and trains a LSTM sequence classification model
def train_sequence_classifier(debug_output=False):
    input_dim = 2000
    cell_dim = 25
    hidden_dim = 25
    embedding_dim = 50
    num_output_classes = 5

    # Input variables denoting the features and label data
    features = sequence.input(shape=input_dim, is_sparse=True)
    label = input(num_output_classes)

    # Instantiate the sequence classification model
    model = create_model(
        features, num_output_classes, embedding_dim, hidden_dim, cell_dim)

    ce = cross_entropy_with_softmax(model, label)
    pe = classification_error(model, label)

    def criterion(input, label):
        z = model(input)
        ce = cross_entropy_with_softmax(z, label)
        pe = classification_error(z, label)
        return (ce, pe)

    rel_path = r"../CNTK/Tests/EndToEndTests/Text/SequenceClassification/Data/Train.ctf"
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), rel_path)

    reader = create_reader(path, True, input_dim, num_output_classes)

    lr_per_sample = learning_rate_schedule(0.05, UnitType.sample)
    # Instantiate the trainer object to drive the model training
    trainer = Trainer(model, (ce, pe),
                      sgd(model.parameters, lr=lr_per_sample))

    # process minibatches and perform model training
    training_progress_output_freq = 10
    log_number_of_parameters(model) ; print()
    progress_printer = ProgressPrinter(freq=training_progress_output_freq, first=10, tag='Training') # more detailed logging
    #progress_printer = ProgressPrinter(tag='Training')

    # Get minibatches of sequences to train with and perform model training
    minibatch_size = 200

    if debug_output:
        training_progress_output_freq = training_progress_output_freq/3

    for i in range(251):
        mb = reader.next_minibatch(minibatch_size)
        trainer.train_minibatch(ce.argument_map(mb[reader.streams.features], mb[reader.streams.labels]))
        progress_printer.update_with_trainer(trainer, with_metric=True)    # log progress
    loss, metric, actual_samples = progress_printer.epoch_summary(with_metric=True)

    import copy

    evaluation_average = copy.copy(
        trainer.previous_minibatch_evaluation_average)
    loss_average = copy.copy(trainer.previous_minibatch_loss_average)

    return evaluation_average, loss_average

if __name__ == '__main__':
    # Specify the target device to be used for computing, if you do not want to
    # use the best available one, e.g.
    # try_set_default_device(cpu())

    error, _ = train_sequence_classifier()
    print("Error: %f" % error)
