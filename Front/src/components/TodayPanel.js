import React, { useState, Component, useRef, useEffect, useReducer } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { openVa } from '../features/vaSlice'
import './TodayPanel.css';

import {ReactComponent as NewVa} from "../logo/newVa.svg"
import {ReactComponent as GenVa} from "../logo/genVa.svg"
import {ReactComponent as VaGen} from "../logo/vaGen.svg"
import {ReactComponent as Popup} from "../logo/popup.svg"
import { set } from 'rsuite/esm/internals/utils/date';

const TodayPanel = () => {
  var openedVa = useSelector((state) => state.va.openedVa);
  const dispatch = useDispatch();
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [vaName, setVaName] = useState('');
  const [selectedVa, setSelectedVa] = useState(null); // 用于选择要打开的VA
  const [popup, setPopup] = useState({});
  const [editingIndex, setEditingIndex] = useState(null);
  const [editId, setEditId] = useState(null);
  const inputRef = useRef(null);
  const [inputValue, setInputValue] = useState("");
  const [vas, setVas] = useState([]);  

  const [, forceUpdate] = useReducer(x => x + 1, 0);
  // 处理关闭弹窗
  const closeModal = () => {
    setIsModalOpen(false);
    setVaName(''); // 清空输入框
  };
  const handleDelete = async (id) => {
    var JsonResult;
    await fetch(`http://127.0.0.1:8888/api/vas?id=${id}`,{
      method:'DELETE',
      mode:'cors',
      headers: {
        "Content-Type": "application/json", // ✅ 确保指定 JSON 类型
      },
    })
    .then((response) => response.text())
    .then((result) => JsonResult = JSON.parse(result))
    .catch((error) => console.error('Error:', error));
    console.log(JsonResult)
    closePopup();
    var temp = vas;
    vas.map((item, index) => {
      if (item.id === id) {
        temp.splice(index, 1);
      }
    });
    setVas(temp);
    console.log(temp)
    forceUpdate();
  };

  const handleRename = (oldName, index) => {
    setEditingIndex(index); // 设置当前编辑的行索引
    setInputValue(oldName); // 设置输入框的值
    closePopup();
  };

  const showPopup = (e, item, index) => {
    e.preventDefault(); // 防止默认行为
  
    setPopup({id:item.id,visible:!popup.visible});
    console.log(popup)
  };

  const openVA = (e, item) => {
    e.preventDefault(); // 防止默认行为
    dispatch(openVa({ name: item.name, id: item.id }));
  }

  const closePopup = () => {
    setPopup({ id:popup.id,visible: false});
  };

  const addNewVa = async () => {
    var JsonResult;
    await fetch(`http://127.0.0.1:8888/api/vas`,{
      method:'POST',
      mode:'cors',
      headers: {
        "Content-Type": "application/json", // ✅ 确保指定 JSON 类型
      },
    })
    .then((response) => response.text())
    .then((result) => JsonResult = JSON.parse(result))
    .catch((error) => console.error('Error:', error));
    console.log(JsonResult)
    var l = vas.length;
    setEditingIndex(l); // 设置当前编辑的行索引
    var temp = vas;
    temp.push(JsonResult['data'])
    setVas(temp)
    setTimeout(() => inputRef.current?.focus(), 0); // 让输入框自动聚焦
  };

  const handleInputChange = (e, index) => {
    setInputValue(e.target.value);
    console.log(inputValue);
  };

  const handleKeyDown = (e, index) => {
    if (e.key === "Enter") {
      var temp = vas;
      if(temp[index]['id'] === openVA['id']){
        dispatch(openVa({ name: e.target.value, id: openVA['id'] }));
      }
      temp[index]['name'] = e.target.value;
      setVas(temp)
      setEditingIndex(null);
    }
  };

  useEffect( () => {
    async function getVas (){
      try {
        const response = await fetch("http://127.0.0.1:8888/api/vas/list", {
          method: "GET",
          mode: "cors",
          headers: {
            "Content-Type": "application/json", // ✅ 确保指定 JSON 类型
          },
        });

        const result = await response.json(); // 直接解析 JSON
        console.log(result);
        setVas(result["data"]); // 更新状态
      } catch (error) {
        console.error("Error:", error);
      }
    }

    getVas();

  }, []);

  const isToday = (timestamp) => {
    // 创建基于Unix时间戳的Date对象（假设timestamp是以秒为单位）
    const date = new Date(timestamp * 1000);
    
    // 获取今天的日期部分（忽略时间）
    const today = new Date();
    today.setHours(0, 0, 0, 0); // 设置时间为当天的开始
    
    // 获取给定日期的零点时间
    const targetDate = new Date(date.getTime());
    targetDate.setHours(0, 0, 0, 0);

    // 比较两个日期是否相同
    return today.getTime() === targetDate.getTime();
}

const isThisWeek = (timestamp)=> {
  // 创建基于Unix时间戳的Date对象（假设timestamp是以秒为单位）
  const date = new Date(timestamp * 1000);
  
  // 获取今天的日期部分，并找到本周的第一天
  const today = new Date();
  const firstDayOfWeek = new Date(today.setDate(today.getDate() - today.getDay()));
  // 注意：在某些地区，一周的第一天是星期一而不是星期天。
  // 如果你认为一周从星期一开始，请使用下面的代码替换上面两行：
  /*
  const firstDayOfWeek = new Date(today.setDate(today.getDate() - ((today.getDay() + 6) % 7)));
  */
  firstDayOfWeek.setHours(0, 0, 0, 0); // 设置时间为当天的开始

  // 获取本周最后一天的日期
  const lastDayOfWeek = new Date(firstDayOfWeek);
  lastDayOfWeek.setDate(lastDayOfWeek.getDate() + 6);
  lastDayOfWeek.setHours(23, 59, 59, 999); // 设置时间为周末的结束

  // 获取给定日期的零点时间
  const targetDate = new Date(date.getTime());
  targetDate.setHours(0, 0, 0, 0);

  // 判断目标日期是否在本周的范围内
  return targetDate >= firstDayOfWeek && targetDate <= lastDayOfWeek;
}



  return (
    <div className="today-panel">
      <div className="va-list">
        <div className="va-list-temp">
        <div className="va-list-title">Today</div>
        {vas.map((item, index) => (
          <div className="va-list-item" style ={{"display":isToday(item.created) ? "":"none"}} onClick={(e) => openVA(e, item)}>
            {editingIndex === index ? (
            <input
              ref={inputRef}
              type="text"
              value={inputValue}
              onChange={(e) => handleInputChange(e, index)}
              onKeyDown={(e) => handleKeyDown(e, index)}
              className="va-list-input"
            />
          ) : (
            <div className="va-list-item-text">{item.name}</div>
          )}
            <button className="va-list-item-button" onClick={(e) => showPopup(e, item, index)}>
              <div className="va-list-item-dot"></div>
              <div className="va-list-item-dot"></div>
              <div className="va-list-item-dot"></div>
            </button>
            <div className="popup" style={{display:item.id === popup.id && popup.visible ? "":"none"}}>
            <Popup/>
            <button onClick={() => handleRename(item.name, index)} style={{"marginTop": "-76px","opacity":"0"}}>
              Rename
            </button>
            <button onClick={() => handleDelete(item.id)} style={{"opacity":"0"}}>Delete</button>
          </div>
          </div>
        ))}
        <div className="va-list-title">This Week</div>
        {vas.map((item, index) => (
          <div className="va-list-item"style ={{"display":!isToday(item.created) && isThisWeek(item.created) ? "":"none"}} onClick={(e) => openVA(e, item)}>
            {editingIndex === index ? (
            <input
              ref={inputRef}
              type="text"
              value={inputValue}
              onChange={(e) => handleInputChange(e, index)}
              onKeyDown={(e) => handleKeyDown(e, index)}
              className="va-list-input"
            />
          ) : (
            <div className="va-list-item-text">{item.name}</div>
          )}
            <button className="va-list-item-button" onClick={(e) => showPopup(e, item, index)}>
              <div className="va-list-item-dot"></div>
              <div className="va-list-item-dot"></div>
              <div className="va-list-item-dot"></div>
            </button>
            <div className="popup" style={{display:item.id === popup.id && popup.visible ? "":"none"}}>
            <Popup/>
            <button onClick={() => handleRename(item.name, index)} style={{"marginTop": "-76px","opacity":"0"}}>
              Rename
            </button>
            <button onClick={() => handleDelete(item.id)} style={{"opacity":"0"}}>Delete</button>
          </div>
          </div>
        ))}

        <div className="va-list-title">Eariler</div>
        {vas.map((item, index) => (
          <div className="va-list-item"style ={{"display":!isThisWeek(item.created) ? "":"none"}} onClick={(e) => openVA(e, item)}>
            {editingIndex === index ? (
            <input
              ref={inputRef}
              type="text"
              value={inputValue}
              onChange={(e) => handleInputChange(e, index)}
              onKeyDown={(e) => handleKeyDown(e, index)}
              className="va-list-input"
            />
          ) : (
            <div className="va-list-item-text">{item.name}</div>
          )}
            <button className="va-list-item-button" onClick={(e) => showPopup(e, item, index)}>
              <div className="va-list-item-dot"></div>
              <div className="va-list-item-dot"></div>
              <div className="va-list-item-dot"></div>
            </button>
            <div className="popup" style={{display:item.id === popup.id && popup.visible ? "":"none"}}>
            <Popup/>
            <button onClick={() => handleRename(item.name, index)} style={{"marginTop": "-76px","opacity":"0"}}>
              Rename
            </button>
            <button onClick={() => handleDelete(item.id)} style={{"opacity":"0"}}>Delete</button>
          </div>
          </div>
          
        ))}
</div>
        <button onClick={addNewVa} className="bottom-va1">
          <NewVa/>
          <div className="bottom-text">New VA</div>
        </button>
        <button className="bottom-va2">
        <VaGen/>
        <div className="bottom-text">VAGen</div>
        <GenVa className="genVa"/>
        </button>

      </div>

    </div>
  );
};

export default TodayPanel;