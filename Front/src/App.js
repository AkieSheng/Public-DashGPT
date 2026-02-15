import React, {useEffect} from 'react';
import { Provider } from 'react-redux';
import {store }from './store';
import HistoryPanel from './components/HistoryPanel';
import TodayPanel from './components/TodayPanel';
import OpenedVaPanel from './components/VaPanel';
import 'typeface-inter';


import './App.css';

function App() {
  useEffect(()=>{
    const screenWidth = window.innerWidth;;  // 屏幕宽度
    const screenHeight = window.innerHeight;; // 屛幕高度

    console.log(`Screen width: ${screenWidth}px`);
    console.log(`Screen height: ${screenHeight}px`);

  
  },[])

  return (
    <Provider store={store} >
      <div className="App" style={{'transform':`scale(${ window.innerWidth/1920 < window.innerHeight/1080 ? window.innerWidth/1920 : window.innerHeight/1080}) `,"transformOrigin":"0 0"}}>
        <TodayPanel />
        <OpenedVaPanel/>
      </div>
    </Provider>
  );
}

export default App;