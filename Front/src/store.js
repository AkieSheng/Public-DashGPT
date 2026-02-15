import { configureStore } from '@reduxjs/toolkit';
import vaReducer from './features/vaSlice';

export const store = configureStore({
  reducer: {
    va: vaReducer,
  },
});