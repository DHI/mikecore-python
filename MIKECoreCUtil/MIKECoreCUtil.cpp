// MIKECoreCUtil.cpp : Defines the exported functions for the DLL.
//

#include "pch.h"
#include "eum.h"
#include "dfsio.h"
#include "MIKECoreCUtil.h"


int dfsGetTimeAxisInfo(LPHEAD pdfs, int* num_timesteps_rtn, double* to_sec_scale_rtn, bool* is_time_equidistant_rtn);


// This is an example of an exported variable
//MIKECORECUTIL_API int nMIKECoreCUtil=0;
//int nMIKECoreCUtil=0;


/** @brief Bulk read the times and data for a dfs0 file, putting it all in
 *         a matrix structure.
 *  @details First column in the result are the times, then a column for each
 *         item in the file. There are as many rows as there are timesteps.
 *         All item data are converted to doubles.
 *  @param[in] pdfs Specifies a reference to the header information structure.
 *  @param[in] fp Specifies a pointer to the file.
 *  @param[in] data Array to store data in, must be of size (num_timesteps * (num_items + 1))
 *  @return
 *  It returns a LONG that indicates possible errors that occurred during or before
 *  the execution of the call. Possible return values are <b>F_NO_ERROR</b> ( = 0), indicating
 *  successful execution or a nonzero value ( != 0) of type @ref FioErrors specifying the exact type
 *  of error.
 */
MIKECORECUTIL_API int ReadDfs0DataDouble(LPHEAD pdfs, LPFILE fp, double* data)
{
  return ReadDfs0ItemsDouble(pdfs, fp, data, NULL, 0);
}


/** @brief Bulk read the times and data for a dfs0 file, putting it all in
 *         a matrix structure.
 *  @details First column in the result are the times, then a column for each
 *         item in the file. There are as many rows as there are timesteps.
 *         All item data are converted to doubles.
 *  @param[in] pdfs Specifies a reference to the header information structure.
 *  @param[in] fp Specifies a pointer to the file.
 *  @param[in] data Array to store data in, must be of size (num_timesteps * (num_items + 1))
 *  @param[in] itemNums Array of item numbers (1-based) to store in data array. Can be null to store all items
 *  @param[in] nitemNums Size of itemNums array. Set to zero to store data for all items
 *  @return
 *  It returns a LONG that indicates possible errors that occurred during or before
 *  the execution of the call. Possible return values are <b>F_NO_ERROR</b> ( = 0), indicating
 *  successful execution or a nonzero value ( != 0) of type @ref FioErrors specifying the exact type
 *  of error.
 */
MIKECORECUTIL_API int ReadDfs0ItemsDouble(LPHEAD pdfs, LPFILE fp, double* data, int* itemNums, int nitemNums)
{
  int rc;

  // Get time axis information - should also work for non-time axis
  int num_timesteps;
  double to_sec_scale;
  bool is_time_equidistant;
  if ((rc = dfsGetTimeAxisInfo(pdfs, &num_timesteps, &to_sec_scale, &is_time_equidistant)))
    return rc;

  double double_delete = dfsGetDeleteValDouble(pdfs);
  float float_delete = dfsGetDeleteValFloat(pdfs);

  // Number of dynamic items
  int num_items = dfsGetNoOfItems(pdfs);

  // Figure out which items to load
  BOOL* itemsToLoad = NULL;
  if (nitemNums > 0)
  {
    itemsToLoad = (BOOL*)malloc(num_items * sizeof(BOOL));
    for (int i = 0; i < num_items; i++)
      itemsToLoad[i] = FALSE;
    for (int i = 0; i < nitemNums; i++)
    {
      int itemIdx = itemNums[i]-1;
      if (itemIdx < 0 || itemIdx >= num_items)
      {
        free (itemsToLoad);
        return F_ERR_DATA;
      }
      itemsToLoad[itemIdx] = TRUE;
    }
  }

  // Store simple type for every item
  SimpleType* itemSimpleTypes = (SimpleType *)malloc(num_items * sizeof(SimpleType));

  /***********************************
   * Dynamic item information
   ***********************************/
  LONG          item_type;                     // Item EUM type id
  LPCTSTR       item_type_str;                 // Name of item type
  LPCTSTR       item_name;                     // Name of item
  LONG          item_unit;                     // Item EUM unit id
  LPCTSTR       item_unit_str;                 // Item EUM unit string
  SimpleType    item_datatype;                 // Simple type stored in item, usually float but can be double

  int maxItemElmts = 1;
  for (int i_item = 1; i_item <= num_items; i_item++)
  {
    LPITEM pitem = dfsItemD(pdfs, i_item);

    // Name, quantity type and unit, and datatype
    rc = dfsGetItemInfo(pitem, &item_type, &item_type_str, &item_name, &item_unit, &item_unit_str, &item_datatype);
    if (rc) 
    {
      if (itemsToLoad) free(itemsToLoad);
      free(itemSimpleTypes);
      return rc;
    }
    itemSimpleTypes[i_item - 1] = item_datatype;

    // Number of elements in item, find the max (in case they are not all dfs0 files, to not do any array-out-of-bounds operations)
    int numElmts = dfsGetItemElements(pitem);
    if (numElmts > maxItemElmts)
      maxItemElmts = numElmts;
  }

  // Buffer for reading from dfs
  float*  dfsdataf = (float *) malloc(maxItemElmts * sizeof(float));
  double* dfsdatad = (double *)malloc(maxItemElmts * sizeof(double));

  // Reset file pointer to first dynamic item-timestep.
  dfsFindBlockDynamic(pdfs, fp);

  int pos = 0;
  double time;
  for (int i = 0; i < num_timesteps; i++)
  {
    for (int j = 0; j < num_items; j++)
    {
      double value;
      if (itemSimpleTypes[j] == UFS_FLOAT)
      {
        rc = dfsReadItemTimeStep(pdfs, fp, &time, dfsdataf);
        float valuef = dfsdataf[0];
        if (valuef != float_delete)
          value = valuef;
        else
          value = double_delete;
      }
      else if (itemSimpleTypes[j] == UFS_DOUBLE)
      {
        rc = dfsReadItemTimeStep(pdfs, fp, &time, dfsdatad);
        value = dfsdatad[0];
      }
      else
      {
        value = double_delete;
      }

      if (rc) 
      {
        if (itemsToLoad) free(itemsToLoad);
        free(itemSimpleTypes);
        free(dfsdataf);
        free(dfsdatad);
        return rc;
      }

      // First column is time, remaining columns are data
      if (j == 0)
      {
        if (is_time_equidistant)
          // TODO: Do we need to add start-time-offset here? Usually zero
          data[pos++] = i * to_sec_scale;
        else
          data[pos++] = time * to_sec_scale;
      }

      if (itemsToLoad == NULL || itemsToLoad[j])
      {
        data[pos++] = value;
      }
    }
  }

  if (itemsToLoad) free(itemsToLoad);
  free(itemSimpleTypes);
  free(dfsdataf);
  free(dfsdatad);

  return 0;
}


/** @brief Bulk write the times and data for a dfs0 file, loading it all from a matrix structure.
 *  @details First column in the data are the times, then a column for each
 *         item in the file. There are as many rows as there are timesteps.
 *         All item data are in doubles, and converted to float if necessary.
 *  @param[in] pdfs Specifies a reference to the header information structure.
 *  @param[in] fp Specifies a pointer to the file.
 *  @param[in] data Array to store data in, must be of size (nTimes * (num_items + 1))
 *  @param[in] nTimes Number of time steps to store, must match size of data array.
 *  @return
 *  It returns a LONG that indicates possible errors that occurred during or before
 *  the execution of the call. Possible return values are <b>F_NO_ERROR</b> ( = 0), indicating
 *  successful execution or a nonzero value ( != 0) of type @ref FioErrors specifying the exact type
 *  of error.
 */
MIKECORECUTIL_API int WriteDfs0DataDouble(LPHEAD pdfs, LPFILE fp, double* data, int nTimes)
{
  int rc;

  // Get time axis information - should also work for non-time axis
  int num_timesteps_file;
  double to_sec_scale;
  bool is_time_equidistant;
  if ((rc = dfsGetTimeAxisInfo(pdfs, &num_timesteps_file, &to_sec_scale, &is_time_equidistant)))
    return rc;
  double to_timeAxis_scale = 1.0 / to_sec_scale;

  double double_delete = dfsGetDeleteValDouble(pdfs);
  float float_delete = dfsGetDeleteValFloat(pdfs);

  // Number of dynamic items
  int num_items = dfsGetNoOfItems(pdfs);

  // Store simple type for every item
  SimpleType* itemSimpleTypes = (SimpleType *)malloc(num_items * sizeof(SimpleType));

  /***********************************
   * Dynamic item information
   ***********************************/
  LONG          item_type;                     // Item EUM type id
  LPCTSTR       item_type_str;                 // Name of item type
  LPCTSTR       item_name;                     // Name of item
  LONG          item_unit;                     // Item EUM unit id
  LPCTSTR       item_unit_str;                 // Item EUM unit string
  SimpleType    item_datatype;                 // Simple type stored in item, usually float but can be double

  int maxItemElmts = 1;
  for (int i_item = 1; i_item <= num_items; i_item++)
  {
    LPITEM pitem = dfsItemD(pdfs, i_item);

    // Name, quantity type and unit, and datatype
    rc = dfsGetItemInfo(pitem, &item_type, &item_type_str, &item_name, &item_unit, &item_unit_str, &item_datatype);
    if (rc)
    {
      free(itemSimpleTypes);
      return rc;
    }
    itemSimpleTypes[i_item - 1] = item_datatype;

    // Number of elements in item, find the max (in case they are not all dfs0 files, to not do any array-out-of-bounds operations)
    int numElmts = dfsGetItemElements(pitem);
    if (numElmts > maxItemElmts)
      maxItemElmts = numElmts;
  }

  // Buffer for writing to dfs
  float*  dfsdataf = (float *) malloc(maxItemElmts * sizeof(float));
  double* dfsdatad = (double *)malloc(maxItemElmts * sizeof(double));
  int*    dfsdatai = (int *)   malloc(maxItemElmts * sizeof(int));
  for (int i = 0; i < maxItemElmts; i++)
  {
    dfsdataf[i] = 0.0f;
    dfsdatad[i] = 0.0;
    dfsdatai[i] = 0;
  }

  // Reset file pointer to first dynamic item-timestep.
  dfsFindBlockDynamic(pdfs, fp);

  int pos = 0;
  for (int i = 0; i < nTimes; i++)
  {
    // First column is time, remaining columns are data
    double time = data[pos++] * to_timeAxis_scale;

    for (int j = 0; j < num_items; j++)
    {
      double value = data[pos++];

      if (itemSimpleTypes[j] == UFS_FLOAT)
      {
        float valuef;
        if (value == double_delete)
          valuef = float_delete;
        else
          valuef = (float)value;

        dfsdataf[0] = valuef;
        rc = dfsWriteItemTimeStep(pdfs, fp, time, dfsdataf);
      }
      else if (itemSimpleTypes[j] == UFS_DOUBLE)
      {
        dfsdatad[0] = value;
        rc = dfsWriteItemTimeStep(pdfs, fp, time, dfsdatad);
      }
      else
      {
        // simple type not supported, write dummy zero data
        rc = dfsWriteItemTimeStep(pdfs, fp, time, dfsdatai);
      }

      if (rc)
      {
        free(itemSimpleTypes);
        free(dfsdataf);
        free(dfsdatad);
        free(dfsdatai);
        return rc;
      }
    }
  }

  free(itemSimpleTypes);
  free(dfsdataf);
  free(dfsdatad);
  free(dfsdatai);

  return 0;
}



/** @brief Get time axis information
 *  @param[in] pdfs Specifies a reference to the header information structure.
 *  @param[out] num_timesteps_rtn Number of time steps in file
 *  @param[out] to_sec_scale_rtn Scale factor for scaling time value to seconds.
 *                               For a non-time axis, no scaling is applied.
 *                               For an equidistant axis, it also includes the size of the time step.
 *  @param[out] is_time_equidistant_rtn Flag indicating if time axis is equidistant
 *  @return
 *  It returns a LONG that indicates possible errors that occurred during or before
 *  the execution of the call. Possible return values are <b>F_NO_ERROR</b> ( = 0), indicating
 *  successful execution or a nonzero value ( != 0) of type @ref FioErrors specifying the exact type
 *  of error.
 */
int dfsGetTimeAxisInfo(LPHEAD pdfs, int* num_timesteps_rtn, double* to_sec_scale_rtn, bool* is_time_equidistant_rtn)
{
  int rc;

  /****************************************
   * Time axis information
   ****************************************/
  TimeAxisType  time_axis_type;                // Type of time axis
  LPCTSTR     start_date, start_time;          // Start date and time for the calendar axes.
  double      tstart = 0;                      // Start time for the first time step in the file. 
  double      tstep = 0;                       // Time step size of equidistant axes
  double      tspan = 0;                       // Time span of non-equidistant axes
  LONG        num_timesteps = 0;               // Number of time steps in file
  LONG        index;                           // Index of first time step. Currently not used, always zero.
  LONG        ntime_unit;                      // Time unit in time axis, EUM unit id
  LPCTSTR     ttime_Unit;                      // Time unit in time axis, EUM unit string
  BOOL        is_time_equidistant = false;
  switch (time_axis_type = dfsGetTimeAxisType(pdfs))
  {
  case F_TM_EQ_AXIS: // Equidistant time axis
    is_time_equidistant = true;
    rc = dfsGetEqTimeAxis(pdfs, &ntime_unit, &ttime_Unit, &tstart, &tstep, &num_timesteps, &index);
    break;
  case F_TM_NEQ_AXIS: // Non-equidistant time axis
    rc = dfsGetNeqTimeAxis(pdfs, &ntime_unit, &ttime_Unit, &tstart, &tspan, &num_timesteps, &index);
    break;
  case F_CAL_EQ_AXIS:  // Equidistant calendar axis
    is_time_equidistant = true;
    rc = dfsGetEqCalendarAxis(pdfs, &start_date, &start_time, &ntime_unit, &ttime_Unit, &tstart, &tstep, &num_timesteps, &index);
    break;
  case F_CAL_NEQ_AXIS: // Non-equidistant calendar axis
    rc = dfsGetNeqCalendarAxis(pdfs, &start_date, &start_time, &ntime_unit, &ttime_Unit, &tstart, &tspan, &num_timesteps, &index);
    break;
  default:
    rc = -1;
    break;
  }

  if (rc == 0)
  {
    *is_time_equidistant_rtn = is_time_equidistant;
    *num_timesteps_rtn = num_timesteps;
    if (ntime_unit == 1400)
    {
      *to_sec_scale_rtn = 1.0;
    }
    else
    {
      const int eumUsec = 1400;
      // Check if time axis is actually a time axis.
      bool ok = eumUnitsEqv(eumUsec, ntime_unit);
      if (ok)
      {
        // Calculate conversion factor to seconds.
        ok = eumConvertUnit(ntime_unit, 1, eumUsec, to_sec_scale_rtn);
      }
      if (!ok)
        *to_sec_scale_rtn = 1.0;
    }
    // For equidistant times, multiply by tstep,
    // so to_sec_scale_rtn is the number of seconds per time step.
    if (is_time_equidistant)
      *to_sec_scale_rtn = (*to_sec_scale_rtn) * tstep;
  }
  else
  {
    *is_time_equidistant_rtn = false;
    *num_timesteps_rtn = 0;
    *to_sec_scale_rtn = 1.0;
  }
  return rc;

}

