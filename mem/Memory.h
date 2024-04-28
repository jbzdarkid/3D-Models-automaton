#pragma once
#include <functional>
#include <vector>

class Memory final {
public:
    Memory(const wchar_t* processName);
    ~Memory();
    
    Memory(const Memory& memory) = delete;
    Memory& operator=(const Memory& other) = delete;

    uint64_t GetBaseAddress() { return _startOfModule; }

    using ScanFunc = std::function<void(uint64_t addr, std::vector<uint8_t>& data)>;
    void AddSigScan(const std::vector<uint8_t>& scanBytes, const ScanFunc& scanFunc);
    void ExecuteSigScans();

    template<class T>
    inline std::vector<T> ReadData(const std::vector<int64_t>& offsets, size_t numItems) {
        std::vector<T> data(numItems);
        ReadDataInternal(data.data(), ComputeOffset(offsets), numItems * sizeof(T));
        return data;
    }

    template <class T>
    inline void WriteData(const std::vector<int64_t>& offsets, const std::vector<T>& data) {
        WriteDataInternal(data.data(), ComputeOffset(offsets), sizeof(T) * data.size());
    }

private:
    void ReadDataInternal(void* buffer, const uintptr_t computedOffset, size_t bufferSize);
    void WriteDataInternal(const void* buffer, uintptr_t computedOffset, size_t bufferSize);
    uintptr_t ComputeOffset(std::vector<int64_t> offsets);
    int Find(const std::vector<uint8_t>& data, const std::vector<uint8_t>& search);

    uint64_t _startOfModule = 0;
    uint64_t _endOfModule = 0;
    void* _handle = nullptr;

    struct SigScan {
        std::vector<uint8_t> scanBytes;
        ScanFunc scanFunc;
        uint64_t addr = 0;
        bool found = false;
    };
    std::vector<SigScan> _sigScans;
};