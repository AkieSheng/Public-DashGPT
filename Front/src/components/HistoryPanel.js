import React from 'react';
import { useSelector } from 'react-redux';

const HistoryPanel = () => {
  const history = useSelector((state) => state.va.history);

  return (
    <div>
      <h2>History</h2>
      <ul>
        {history.map((item, index) => (
          <li key={index}>{item}</li>
        ))}
      </ul>
      <button onClick={() => console.log('Create VA')}>Create VA</button>
      <button onClick={() => console.log('Open VA')}>Open VA</button>
    </div>
  );
};

export default HistoryPanel;