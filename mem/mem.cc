#include <stdio.h> // fprintf
#include <stdint.h> // uintptr_t
#include <windows.h> // everything else
#include <psapi.h> // Module processing. Has to be after windows.h
#include <tlhelp32.h> // getting the PID

// http://stackoverflow.com/q/1387064
void throwError() {
  wchar_t message[256];
  FormatMessageW(4096, NULL, GetLastError(), 1024, message, 256, NULL);
  fprintf(stderr, "Error: %ls\n", message);
  exit(EXIT_FAILURE);
}

// https://github.com/erayarslan/WriteProcessMemory-Example
// http://stackoverflow.com/q/32798185
// http://stackoverflow.com/q/36018838
int main(int argc, char *argv[]) {
  if (argc < 2) {
    fprintf(stderr, "Usage: mem <trans|rot> [x y z]\n");
    exit(EXIT_FAILURE);
  }
  DWORD pid = NULL;
  HMODULE module_list[1024];
  DWORD num_results;
  char name[64];
  uintptr_t base_addr;
  PROCESSENTRY32 entry;
  entry.dwSize = sizeof(entry);
  HANDLE snapshot = CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0);

  while (Process32Next(snapshot, &entry)) {
    if (wcscmp(entry.szExeFile, L"hlmv.exe") == 0) {
      pid = entry.th32ProcessID;
      break;
    }
  }

  HANDLE handle = nullptr;
  if (pid != NULL) handle = OpenProcess(PROCESS_ALL_ACCESS, FALSE, pid);
  if (!handle) {
    fprintf(stderr, "Couldn't find HLMV. Is it open?\n");
    exit(EXIT_FAILURE);
  }
  EnumProcessModules(handle, module_list, sizeof(module_list) / sizeof(HMODULE), &num_results);
  for (int i = 0; i < num_results / sizeof(HMODULE); i++) {
    GetModuleBaseNameA(handle, module_list[i], name, sizeof(name));
    if (strcmp(name, "hlmv.exe") == 0) {
      base_addr = (uintptr_t)module_list[i];
      break; // All that setup just to get the base address and handle
    }
  }

  LPVOID offset;
  if (strcmp(argv[1], "rot") == 0) { // Absolute Rotation
    offset = (LPVOID)(base_addr + 0x23C510);
  } else if (strcmp(argv[1], "trans") == 0) { // Absolute Translation
    offset = (LPVOID)(base_addr + 0x23C51C);
  } else if (strcmp(argv[1], "color") == 0) { // Background color
    offset = (LPVOID)(base_addr + 0x23F214);
  } else if (strcmp(argv[1], "bg") == 0) { // Enable Background
    offset = (LPVOID)(base_addr + 0x23F1DC);
  } else if (strcmp(argv[1], "nm") == 0) { // Normal Maps
    offset = (LPVOID)(base_addr + 0x23F18F);
  } else if (strcmp(argv[1], "spec") == 0) { // Specular
    offset = (LPVOID)(base_addr + 0x23F191);
  } else if (strcmp(argv[1], "ob") == 0) { // Overbrightening
    offset = (LPVOID)(base_addr + 0x23F23E);
  } else if (strcmp(argv[1], "lrot") == 0) { // Light Rotation
    offset = (LPVOID)(base_addr + 0x2401B8);
  } else {
    fprintf(stderr, "Unknown type parameter: %s\n", argv[1]);
    exit(EXIT_FAILURE);
  }

  if (argc == 2) {
    if (strcmp(argv[1], "bg") == 0) {
      int background;
      if (ReadProcessMemory(handle, offset, &background, sizeof(background), NULL)) {
        fprintf(stdout, "%d", background);
      } else {
        throwError();
      }
    } else if (
      strcmp(argv[1], "trans") == 0 ||
      strcmp(argv[1], "rot") == 0 ||
      strcmp(argv[1], "lrot") == 0
    ) {
      float values[3];
      if (ReadProcessMemory(handle, offset, &values, sizeof(values), NULL)) {
        fprintf(stdout, "%f %f %f\n", values[0], values[1], values[2]);
      } else {
        throwError();
      }
    } else if (strcmp(argv[1], "color") == 0) {
      float values[4];
      if (ReadProcessMemory(handle, offset, &values, sizeof(values), NULL)) {
        fprintf(stdout, "%f %f %f %f\n", values[0], values[1], values[2], values[3]);
      } else {
        throwError();
      }
    }
  } else if (argc == 3) {
    int background = atoi(argv[2]);
    if (!WriteProcessMemory(handle, offset, &background, sizeof(background), NULL)) {
      throwError();
    }
  } else if (argc == 5) {
    float values[3];
    values[0] = atof(argv[2]);
    values[1] = atof(argv[3]);
    values[2] = atof(argv[4]);
    if (!WriteProcessMemory(handle, offset, &values, sizeof(values), NULL)) {
      throwError();
    }
  } else if (argc == 6) {
    float values[4];
    values[0] = atof(argv[2]);
    values[1] = atof(argv[3]);
    values[2] = atof(argv[4]);
    values[3] = atof(argv[5]);
    if (!WriteProcessMemory(handle, offset, &values, sizeof(values), NULL)) {
      throwError();
    }
  }
  CloseHandle(handle);
}