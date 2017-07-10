//
// Copyright (c) Microsoft. All rights reserved.
// Licensed under the MIT license. See LICENSE.md file in the project root for full license information.
//

// Use this header to resolve symbols when only header is used from CNTKV2Library (without binary dependency on .so, .dll).

#pragma once

#include "Basics.h"

namespace CNTK {

    template <class E>
    __declspec_noreturn void ThrowFormatted(const char* format, ...)
    {
        va_list args;
        va_start(args, format);
        Microsoft::MSR::CNTK::ThrowFormattedVA<E>(format, args);
        va_end(args);
    }

    template __declspec_noreturn void ThrowFormatted<std::runtime_error>(const char* format, ...);
    template __declspec_noreturn void ThrowFormatted<std::logic_error>(const char* format, ...);
    template __declspec_noreturn void ThrowFormatted<std::invalid_argument>(const char* format, ...);

    namespace Internal
    {
        bool IsReversingTensorShapesInErrorMessagesEnabled()
        {
            return false;
        }
    }
}
