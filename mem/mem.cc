#define _CRT_SECURE_NO_WARNINGS
#include "Memory.h"
#include <Windows.h>

/* How to auto-attach (e.g. when mem is launched from the python scripts):
0. Make sure you have the Just In Time Debugger installed & enabled in visual studio
1. Open regedit
2. Navigate to HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\mem.exe
3. Set debugger = vsjitdebugger.exe (REG_SZ)
4. Navigate to HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\AeDebug
5. Set Auto = 1 (REG_SZ)
*/

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

std::vector<int64_t> ParseOffsets(int argc, char *argv[]) {
    if (argc < 3) {
        fprintf(stderr, "Missing read/write offsets (argument 3)");
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

    return offsets;
}

void PrintHexString(const std::vector<uint8_t>& bytes) {
    for (const uint8_t byte : bytes) {
        printf("%02X", byte);
    }
    printf(" ");
}

int main(int argc, char *argv[]) {
    if (argc <= 2) {
        fprintf(stderr, "Usage:\n");
        fprintf(stderr, "mem sigscan <scan bytes> [scan bytes] [scan bytes] ...\n");
        fprintf(stderr, "mem read <num bytes> <hex offset> [hex offset] [hex offset] ...\n");
        fprintf(stderr, "mem write <hex data> <hex offset> [hex offset] [hex offset] ...\n");
        exit(EXIT_FAILURE);
    }

    Memory memory(L"hlmv"); // Prefix search, matches either hlmv.exe *or* hlmvplusplus.exe

    if (strcmp(argv[1], "sigscan") == 0) {
        printf("%016llX ", memory.GetBaseAddress());

        for (int i = 2; i < argc; i++) {
            memory.AddSigScan(ParseHexString(argv[i]), [](uint64_t addr, std::vector<uint8_t>& data) {
                if (data.size() == 0) {
                    printf("  "); // two empty objects
                } else {
                    // If we found a match, limit to 100 bytes.
                    data.resize(100);
                    printf("%016llX ", addr);
                    PrintHexString(data);
                }
            });
        }

        memory.ExecuteSigScans();

    } else if (strcmp(argv[1], "read") == 0) {
        size_t numBytes = 0;
        int retval = sscanf(argv[2], "%zd", &numBytes);
        if (retval != 1) {
            fprintf(stderr, "Could not parse number of bytes to read: '%s'", argv[2]);
            exit(EXIT_FAILURE);
        }

        std::vector<int64_t> offsets = ParseOffsets(argc, argv);

        PrintHexString(memory.ReadData<uint8_t>(offsets, numBytes));

    } else if (strcmp(argv[1], "write") == 0) {
        std::vector<uint8_t> bytes = ParseHexString(argv[2]);
        std::vector<int64_t> offsets = ParseOffsets(argc, argv);

        memory.WriteData<uint8_t>(offsets, bytes);

    } else {
        fprintf(stderr, "Unknown command '%s'", argv[1]);
        exit(EXIT_FAILURE);
    }
}