// The following ifdef block is the standard way of creating macros which make exporting
// from a DLL simpler. All files within this DLL are compiled with the MIKECORECUTIL_EXPORTS
// symbol defined on the command line. This symbol should not be defined on any project
// that uses this DLL. This way any other project whose source files include this file see
// MIKECORECUTIL_API functions as being imported from a DLL, whereas this DLL sees symbols
// defined with this macro as being exported.
#ifdef MIKECORECUTIL_EXPORTS
#define MIKECORECUTIL_API __declspec(dllexport)
#else
#define MIKECORECUTIL_API __declspec(dllimport)
#endif

#include <dfsio.h>

//MIKECORECUTIL_API int nMIKECoreCUtil;

extern "C" MIKECORECUTIL_API int ReadDfs0DataDouble(LPHEAD pdfs, LPFILE fp, double* data);
extern "C" MIKECORECUTIL_API int ReadDfs0ItemsDouble(LPHEAD pdfs, LPFILE fp, double* data, int* itemNums, int nitemNums);
extern "C" MIKECORECUTIL_API int WriteDfs0DataDouble(LPHEAD pdfs, LPFILE fp, double* data, int nTimes);
