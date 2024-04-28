#include "Memory.h"

#define WIN32_LEAN_AND_MEAN
#define NOMINMAX
#include <Windows.h>

#include <memoryapi.h>
#include <processthreadsapi.h>
#include <Psapi.h>
#include <TlHelp32.h>

#include <vector>

// Code stolen from https://github.com/jbzdarkid/witness-trainer

#define assert(condition, message) \
    if (!(condition)) { \
        fprintf(stderr, "Assertion failed on line %d: %s", __LINE__, message); \
        exit(EXIT_FAILURE); \
    } \
    do {} while(0)


Memory::Memory(const wchar_t* processName) {
    PROCESSENTRY32 entry = {};
    entry.dwSize = sizeof(entry);
    HANDLE snapshot = CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0);
    while (Process32Next(snapshot, &entry)) {
        if (wcsncmp(processName, entry.szExeFile, wcslen(processName)) == 0) {
            _handle = OpenProcess(PROCESS_ALL_ACCESS, FALSE, entry.th32ProcessID);
            break;
        }
    }

    assert(_handle, "Could not find HLMV/HLMV++, is it open?");

    DWORD unused;
    HMODULE modules[1] = {};
    EnumProcessModules(_handle, &modules[0], sizeof(HMODULE), &unused);
    assert(modules[0], "Failed to enumerate process modules");
    MODULEINFO moduleInfo;
    GetModuleInformation(_handle, modules[0], &moduleInfo, sizeof(moduleInfo));

    _startOfModule = reinterpret_cast<uint64_t>(moduleInfo.lpBaseOfDll);
    _endOfModule = _startOfModule + moduleInfo.SizeOfImage;
    assert(_startOfModule, "Start of module was 0");
    assert(_endOfModule > _startOfModule, "Module size was 0");
}

Memory::~Memory() {
    if (_handle) CloseHandle(_handle);
}

// Small wrapper for non-failing scan functions
void Memory::AddSigScan(const std::vector<uint8_t>& scanBytes, const ScanFunc& scanFunc) {
    _sigScans.push_back({scanBytes, scanFunc, false});
}

constexpr size_t BUFFER_SIZE = 0x10000; // 10 KB or so
void Memory::ExecuteSigScans() {
    size_t found = 0;
    std::vector<uint8_t> buff;
    buff.resize(BUFFER_SIZE + 0x100); // padding in case the sigscan is past the end of the buffer

    for (uintptr_t i = _startOfModule; i < _endOfModule; i += BUFFER_SIZE) {
        ReadDataInternal(&buff[0], i, buff.size());
        for (SigScan& sigScan : _sigScans) {
            if (sigScan.found) continue;
            int index = Find(buff, sigScan.scanBytes);
            if (index == -1) continue;

            // Make a copy of the buffer so that we can call the sigscan callbacks in input order.
            sigScan.scanBytes = std::vector<uint8_t>(buff.begin() + index, buff.end());
            sigScan.addr = i + index;
            sigScan.found = true;
            found++;
        }

        if (found == _sigScans.size()) break;
    }

    for (SigScan& sigScan : _sigScans) {
        if (sigScan.found) {
            sigScan.scanFunc(sigScan.addr, sigScan.scanBytes);
        } else {
            std::vector<uint8_t> empty;
            sigScan.scanFunc(0, empty);
        }
    }
}

int Memory::Find(const std::vector<uint8_t>& data, const std::vector<uint8_t>& search) {
    const uint8_t* dataBegin = &data[0];
    const uint8_t* searchBegin = &search[0];
    size_t maxI = data.size() - search.size();
    size_t maxJ = search.size();

    for (int i=0; i<maxI; i++) {
        bool match = true;
        for (size_t j=0; j<maxJ; j++) {
            if (*(dataBegin + i + j) == *(searchBegin + j)) {
                continue;
            }
            match = false;
            break;
        }
        if (match) return i;
    }
    return -1;
}

void Memory::ReadDataInternal(void* buffer, const uintptr_t computedOffset, size_t bufferSize) {
    assert(bufferSize > 0, "Attempted to read 0 bytes");
    assert(buffer, "Attempted to read into a null buffer");
    if (!_handle) return;
    ReadProcessMemory(_handle, (void*)computedOffset, buffer, bufferSize, nullptr);
}

void Memory::WriteDataInternal(const void* buffer, uintptr_t computedOffset, size_t bufferSize) {
    assert(bufferSize > 0, "Attempted to write 0 bytes");
    assert(buffer, "Attempted to write from a null buffer");
    if (!_handle) return;
    WriteProcessMemory(_handle, (void*)computedOffset, buffer, bufferSize, nullptr);
}

uintptr_t Memory::ComputeOffset(std::vector<int64_t> offsets) {
    assert(offsets.size() > 0, "Attempted to compute 0 offsets");
    assert(offsets.front() != 0, "First offset to compute cannot be 0");

    // Leave off the last offset, since it will be either read/write, and may not be of type uintptr_t.
    const int64_t finalOffset = offsets.back();
    offsets.pop_back();

    uintptr_t cumulativeAddress = _startOfModule;
    for (const int64_t offset : offsets) {
        cumulativeAddress += offset;

        uintptr_t computedAddress = 0;
        ReadDataInternal(&computedAddress, cumulativeAddress, sizeof(computedAddress));
        if (computedAddress) {
            cumulativeAddress = computedAddress;
            continue;
        }

        assert(computedAddress != 0, "nullptr encountered in pointer path, so we tried to dereference NULL.");

        MEMORY_BASIC_INFORMATION info;
        if (!VirtualQuery(reinterpret_cast<LPVOID>(cumulativeAddress), &info, sizeof(info))) {
            assert(false, "Failed to read process memory, possibly because cumulativeAddress was too large.");
        } else {
            assert(info.State == MEM_COMMIT, "Attempted to read unallocated memory.");
            assert(info.AllocationProtect & 0xC4, "Attempted to read unreadable memory."); // 0xC4 = PAGE_EXECUTE_READWRITE | PAGE_EXECUTE_WRITECOPY | PAGE_READWRITE
            assert(false, "Failed to read memory for some as-yet unknown reason.");
        }
        return 0;
    }

    return cumulativeAddress + finalOffset;
}

