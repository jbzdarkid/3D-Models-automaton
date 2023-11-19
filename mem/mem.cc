/*
#include <stdio.h> // fprintf
#include <stdint.h> // uintptr_t
#include <windows.h> // everything else
#include <psapi.h> // Module processing. Has to be after windows.h
#include <tlhelp32.h> // getting the PID
*/

#define _CRT_SECURE_NO_WARNINGS
#include "Memory.h"
#include <Windows.h>

// https://stackoverflow.com/q/1387064
// Move this to Memory to replace cassert?
void throwError() {
    wchar_t message[256];
    FormatMessageW(4096, NULL, GetLastError(), 1024, message, 256, NULL);
    fprintf(stderr, "Error: %ls\n", message);
    exit(EXIT_FAILURE);
}

std::vector<uint8_t> ParseHexString(const char* str) {
    size_t length = strlen(str) / 2; // 1 byte per 2 hex characters
    std::vector<uint8_t> bytes(length);
    for (int j = 0; j < length; j++) {
        int32_t scan = 0;
        int32_t retval = sscanf(&str[j*2], "%02X", &scan);
        if (retval != 1 || scan < 0x00 || scan > 0xFF) {
            fprintf(stderr, "Error: Failed to parse hex string %s", str);
            exit(EXIT_FAILURE);
        }
        bytes[j] = scan;
    }
    return bytes;
}

void PrintHexString(const std::vector<uint8_t>& bytes) {
    for (const uint8_t byte : bytes) {
        printf("%02X", byte);
    }
}

int main(int argc, char *argv[]) {
    if (argc <= 2) {
        fprintf(stderr, "Usage:\n");
        fprintf(stderr, "mem sigscan [hex bytes]\n");
        fprintf(stderr, "mem read [num bytes] [hex address]");
        fprintf(stderr, "mem write [hex address] [hex bytes]");
        exit(EXIT_FAILURE);
    }

    if (strcmp(argv[1], "sigscan") == 0) {
        Memory memory(L"hlmv.exe");
        for (int i = 2; i < argc; i++) {
            memory.AddSigScan(ParseHexString(argv[i]), [&](int64_t offset, int index, const std::vector<uint8_t>& data) {
                auto start = data.begin() + index;
                auto end = start + min(100, data.size() - index); // 100 bytes or end of data
                PrintHexString(std::vector<uint8_t>(start, end));
                printf("\n");
            });
        }

        memory.ExecuteSigScans();

    } else if (strcmp(argv[1], "read") == 0) {
        Memory memory(L"hlmv.exe");

        int32_t numBytes = 0;
        int retval = sscanf(argv[2], "%d", &numBytes);
        if (retval != 1) {
            fprintf(stderr, "Could not parse number of bytes to read: '%s'", argv[2]);
            exit(EXIT_FAILURE);
        }

        std::vector<int64_t> offsets;
        for (int i = 3; i < argc; i++) {
            int64_t offset = 0;
            int retval = sscanf(argv[i], "%lld", &offset);
            if (retval != 1) {
                fprintf(stderr, "Could not parse offset %d: '%s'", (i - 3), argv[i]);
                exit(EXIT_FAILURE);
            }

            offsets.push_back(offset);
        }

        PrintHexString(memory.ReadData<uint8_t>(offsets, numBytes));

    } else if (strcmp(argv[1], "write") == 0) {
        Memory memory(L"hlmv.exe");

        std::vector<int64_t> offsets;
        int64_t offset = 0;
        int retval = sscanf(argv[2], "%lld", &offset);
        if (retval != 1) {
            fprintf(stderr, "Could not parse offset: '%s'", argv[2]);
            exit(EXIT_FAILURE);
        }

        offsets.push_back(offset);

        if (argc < 3) {
            fprintf(stderr, "Missing write bytes (argument 3)");
            exit(EXIT_FAILURE);
        }

        std::vector<uint8_t> bytes = ParseHexString(argv[3]);
        memory.WriteData<uint8_t>(offsets, bytes);

    } else {
        fprintf(stderr, "Unknown command '%s'", argv[1]);
        exit(EXIT_FAILURE);
    }
}