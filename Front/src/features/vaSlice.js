// src/features/vaSlice.js
import { createSlice } from '@reduxjs/toolkit';

const vaSlice = createSlice({
  name: 'va',
  initialState: {
    openedVa: null, // 当前打开的VA
  },
  reducers: {
    openVa: (state, action) => {
      state.openedVa = action.payload; // 设置当前打开的VA
    },
  },
});

export const { openVa } = vaSlice.actions;
export default vaSlice.reducer; // 默认导出reducer