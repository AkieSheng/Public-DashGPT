import React, { useEffect, useState, useReducer, use , Component, useRef} from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { Uploader } from 'rsuite';
import vegaEmbed from "vega-embed";
import Modal from "react-bootstrap/Modal";
import Button from "react-bootstrap/Modal";

import './OpenedVaPanel.css';

import {ReactComponent as EditNote} from '../logo/note.svg'
import {ReactComponent as Calendar} from '../logo/calendar.svg'
import {ReactComponent as ListButton}  from '../logo/listButton.svg'
import {ReactComponent as Overview}  from '../logo/overview.svg'
import {ReactComponent as Telcodb}  from '../logo/telcodb.svg'
import {ReactComponent as Plan}  from '../logo/plan.svg'
import {ReactComponent as Requirements}  from '../logo/requirements.svg'
import {ReactComponent as Chat}  from '../logo/chat.svg'
import {ReactComponent as DataRequirements}  from '../logo/dataRequirement.svg'
import {ReactComponent as VisRequirements}  from '../logo/visRequirement.svg'
import {ReactComponent as IntRequirements}  from '../logo/intRequirement.svg'
import {ReactComponent as Delete}  from '../logo/delete.svg';
import {ReactComponent as Pipeline} from '../logo/pipeline.svg';
import {ReactComponent as Database} from '../logo/database.svg';
import { set } from 'rsuite/esm/internals/utils/date';
import {ReactComponent as DesignRequirement} from '../logo/designRequirement.svg'
import {ReactComponent as Analy} from '../logo/analy.svg'
import {ReactComponent as AnalyTick} from '../logo/analyTIck.svg'
import {ReactComponent as AnalyPlan} from '../logo/analyPlan.svg'
import {ReactComponent as Tri} from '../logo/tri.svg'
import {ReactComponent as DeleteCross} from '../logo/deleteCross.svg'
import {ReactComponent as UpTri} from '../logo/upTri.svg'
import {ReactComponent as PipelinePanel} from '../logo/pipelinePanel.svg'
import {ReactComponent as Logs} from '../logo/logs.svg'
import {ReactComponent as GreenTick} from '../logo/greenTick.svg'
import {ReactComponent as Warning} from '../logo/warning.svg'
import {ReactComponent as Loading} from '../logo/loading.svg'
import {ReactComponent as Refresh} from '../logo/refresh.svg'
import {ReactComponent as Unfold} from '../logo/unfold.svg'

const OpenedVaPanel = () => {
  var openedVa = useSelector((state) => state.va.openedVa);

  const levelList = ["overview", "explore", "detail", "insight"]
  const categoryList = ["retrieving values", "filtering", "computing derived values",  "finding extrema", "sorting", "determining ranges", "characterizing distributions", "finding anomalies", "clustering", "correlating"]
  
  const [desc, setDesc] = useState('desc');
  const [goal, setGoal] = useState('goal');

  const [openedVaDetail, setOpenedVaDetail] = useState(
    []
  );
  const [listVaDetail, setListVaDetail] = useState(true)
  const [intermediateTable, setIntermediateTable] = useState({
    "code": 200,
    "message": "Databased uploaded",
    "data": [
      {
        "table": "数据库中表的名称",
        "columns": [
          {
            "column": "列的名称",
            "dtype": "SQL 数据类型"
          }, 
        ]
      }
    ]
  })
  const [listInter, setListInter] = useState(false);
  const [vaPlan, setVaPlan] = useState({'graph':"",'path':""});

  const arrayLength = 10000;
  const [listedDetail, setListedDetail] = useState(() => Array(arrayLength).fill(false));
  const [listedDetailI, setListedDetailI] = useState(() => Array(arrayLength).fill(false));
  const [designRequirements, setDesignRequirements] = useState({})
  const [designRequirementsChosen, setDesignRequirementsChosen] = useState("data");

  const [tasks, setTasks] =useState([
    {"Category":"b",
      "Data":["Location_Data.long","t2.c2","t2.c2","Loacation_Data.test33","table_name.test_column"],
      "method":"s",
      "priority":1,
      "Level":"b",
      "visualization":"ab",
      "Interactions":[{"action":["Click"],"position":"c","response":"c"},{"action":["a"],"position":"d","response":"c"},{"action":["a"],"position":"f","response":"c"}],
      "Source":"a",
      "id":1,
    },
    {"Category":"b",
      "Data":["a","b"],
      "method":"s",
      "priority":1,
      "Level":"b",
      "visualization":"A bar chart showing the distribution of customer status and a scatter plot showing churn score versus average monthly GB download.",
      "Interactions":[{"action":["Click"],"position":"c","response":"c"},{"action":["a"],"position":"d","response":"c"},{"action":["a","b"],"position":"f","response":"c"}],
      "Source":"a",
      "id":2,
    },
    {"Category":"b",
      "Data":["a","b"],
      "method":"s",
      "priority":1,
      "Level":"b",
      "visualization":"ab",
      "Interactions":[{"action":["a"],"position":"c","response":"c"},{"action":["a"],"position":"d","response":"c"},{"action":["a"],"position":"f","response":"c"}],
      "Source":"a",
      "id":3,
    },
  ])
  const [taskChosen, setTaskChosen] = useState(1);
  const [views, setViews] = useState([])

  const [uploadStatus, setUploadStatus] = useState('');

  const [, forceUpdate] = useReducer(x => x + 1, 0);

  const descInput = (e) => {
    setDesc(e.target.value);
  }

  const goalInput = (e) => {
    setGoal(e.target.value);
  }
  const listDetail = (index) => {
    var listedDetailTemp = listedDetail;
    listedDetailTemp[index] = !listedDetailTemp[index];
    setListedDetail(listedDetailTemp);
    console.log(listedDetail)
    forceUpdate()
  }

  const listDetailI = (index) => {
    var listedDetailTemp = listedDetailI;
    listedDetailTemp[index] = !listedDetailTemp[index];
    setListedDetailI(listedDetailTemp);
    forceUpdate()
  }

  const chooceRequirement = (kind) => {
    setDesignRequirementsChosen(kind);
  }

  const [nameEdit, setNameEdit] = useState(false)

  const onNameInput = () => {
    var nameedit = nameEdit;
    setNameEdit(!nameedit) 
  }

  const [goalEdit, setGoalEdit] = useState(false)

  const onGoalInput = () => {
    var goaledit = goalEdit;
    setGoalEdit(!goaledit)
  }

  const [descEdit, setDescEdit] = useState(false)

  const onDescInput = () => {
    var descedit = descEdit;
    setDescEdit(!descedit)
  }

  const [viewTitleEdit, setViewTitleEdit] = useState(false)

  const onViewTitleInput = () => {
    var viewtitleedit = viewTitleEdit;
    setViewTitleEdit(!viewtitleedit)
  }

  const [visEdit, setVisEdit] = useState(false)

  const onVisInput = () => {
    var visedit = visEdit;
    setVisEdit(!visedit)
  }

  const [dsEdit, setDsEdit] = useState(false)

  const onDsInput = () => {
    const dsedit = dsEdit;
    setDsEdit(!dsedit)
  }

  const [intAndCorEdit, setIntAndCorEdit] = useState(false)

  const onIntAndCorInput = () => {
    const intAndCorEdit = intAndCorEdit;
    setIntAndCorEdit(!intAndCorEdit)
  }

  const [selectedFile, setSelectedFile] = useState(null);
  // 处理文件上传
  const handleFileUpload = async (file) => {

      const formData = new FormData();
      formData.append("file", file);
      for (let [key, value] of formData.entries()) {
        console.log(key, value); // 应该输出 "file" 和文件对象
      }
      console.log(file)
      const response = await fetch(`http://127.0.0.1:8888/api/database?id=${openedVa.id}`,{
        method:'POST',
        mode:'cors',
        body: formData,
      })
      
      const JsonResult = await response.json();

      console.log(JsonResult)
      setOpenedVaDetail(JsonResult.data)
  };

  const openFileDialog = () => {
    document.getElementById('customFileInput').click();
  };

  const handleFileChange = (event) => {
    const file = event.target.files[0];
    console.log(file)
    if(file){
      setSelectedFile(file);
      setUploadStatus(`Selected file: ${file.name}`);
      handleFileUpload(file);
    };

  };

  const deleteRequirement = (index) => {
    var designRequirementsTemp = designRequirements;
    designRequirementsTemp.splice(index, 1);
    setDesignRequirements(designRequirementsTemp);
    console.log(designRequirements)
    forceUpdate()
  };

  const openVaDetail = () => {
    setListVaDetail(!listVaDetail)
  };

  const openInter = () =>{
    setListInter(!listInter)
  };

  const addPriority = ()=>{
    if(tasks[taskChosen]["priority"]>0){
      var taskTemp = tasks;
      taskTemp[taskChosen]["priority"] = taskTemp[taskChosen]["priority"] + 1;
      setTasks(taskTemp);
      forceUpdate();
    }
  };

  const minusPriority = ()=>{
    if(tasks[taskChosen]["priority"]>0){
      var taskTemp = tasks;
      taskTemp[taskChosen]["priority"] = taskTemp[taskChosen]["priority"] - 1;
      setTasks(taskTemp);
      forceUpdate();
    }
    console.log("minus")
  };

  const deleteData = (index)=>{
    var taskTemp = tasks;
    taskTemp[taskChosen]["Data"].splice(index, 1);
    setTasks(taskTemp);
    console.log(index)
    forceUpdate();
  }

  const [listCategory, setListCategory] = useState(false);
  const [CategoryChosen, setCategoryChosen] = useState(0);

  const [listLevel, setListLevel] = useState(false);
  const [LevelChosen, setLevelChosen] = useState(0);

  const [InteractionChosen, setInteractionChosen] = useState(0);
  const [actionChosen, setActionChosen] = useState(0);

  const [listAction, setListAction] = useState(false);

  const [CategoryEdit, setCategoryEdit] = useState(false);
  const [methodEdit, setMethodEdit] = useState(false);
  const [planEdit, setPlanEdit] = useState(false);
  const [levelEdit, setLevelEdit] = useState(false);
  const [actionEdit, setActionEdit] = useState(false);
  const [positionEdit, setPositionEdit] = useState(false);
  const [responseEdit, setResponseEdit] = useState(false);
  const [sourceEdit, setSourceEdit] = useState(false);

  const [stage, setStage] = useState(1);
  const [step, setStep] = useState(10);

  const [addData, setAddData] = useState(false)

  const [logs, setLogs] = useState([
    {"Stage":"DB Understanding","Raw":"asd", "status":"done"},
    {"Stage":"DB Understanding","Raw":"asdasdsa", "status":"done"},
    {"Stage":"DB Understanding","Raw":"sdwqe", "status":"warning"},
    {"Stage":"DB Understanding","Raw":"qwer", "status":"done"},
    {"Stage":"Requirements","Raw":"qwer", "status":"loading"},
  ])

  useEffect(() => {

  }, [openedVa]);

  useEffect(() => {
    const link = document.createElement('link');
    link.href = 'https://fonts.googleapis.com/css2?family=Azeret+Mono&display=swap';
    link.rel = 'stylesheet';
    document.head.appendChild(link);
  }, []);

  const chartRef = useRef();

  const [vlcodes,setVlcodes] = useState({
    "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
    "description": "A simple bar chart with embedded data.",
    "data": {
      "values": [
        {"a": "A", "b": 28}, {"a": "B", "b": 55}, {"a": "C", "b": 43},
        {"a": "D", "b": 91}, {"a": "E", "b": 81}, {"a": "F", "b": 53},
        {"a": "G", "b": 19}, {"a": "H", "b": 87}, {"a": "I", "b": 52}
      ]
    },
    "mark": "bar",
    "encoding": {
      "x": {"field": "a", "type": "nominal", "axis": {"labelAngle": 0}},
      "y": {"field": "b", "type": "quantitative"}
    }
  }
  );


  useEffect(() => {

    if(opened) vegaEmbed("#vlchart", vlcodes);
  }, [openedVa]);

  const [showCode, setShowCode] = useState(false);
  const [code, setCode0] = useState("")

  const [sqls, setSqls] = useState([])

  const [update, setUpdate] = useState(true);
  const [viewChosen, setViewChosen] = useState(0);
  const [dbDescription, setDBDescription] = useState("")

  const Initial = ()=>{
      setDesc("")
      setGoal("")
      setDBDescription("")
      setOpenedVaDetail([
        {
          "table": "",
          "columns": [
            {
              "column": "",
              "dtype": ""
            },
          ]
        },
      ])
      setDesignRequirements({'data':[],'interaction':[],'visualization':[]})
      setTasks([{"Category":"filtering","method":"","Data":[""],"level":"","visualization":"","Interactions":[],"source":"","priority":1,"id":1}])
      setTaskChosen(0)
      setViewChosen(0)
      setInteractionChosen(0)
      setVaPlan({"path":"","graph":[]})
      setViews([{'interactions':[{'verb':"",'object':"",'effect':{'description':""},"params":[{"name":"","select":{}}]}],'level':"overview",'id':'1','usingParams':[],'visualization':{'description':""}, 'fields':[""]}])
      setSqls("")
      setVlcodes({})
      setLogs([])
      forceUpdate()
  }
  const upDateVA = (data)=>{
      if(data.desc) setDesc(data.desc)
      if(data.goal) setGoal(data.goal)
      if('dataset' in data && 'description' in data) setDBDescription(data.dataset.description)
      if('dataset' in data && 'tables' in data.dataset) setOpenedVaDetail(data.dataset.tables)
      if('requirements'in data) setDesignRequirements(data.requirements)
      var temp = [];
      if('tasks' in data){
        data.tasks.map((task, index) => {
          temp.push({"Category":task.type,"method":task.method,"Data":task.data,"level":"","visualization":"","Interactions":[],"source":"","priority":task.priority,"id":task.taskId})
        })
        if(temp) setTasks(temp)
      }
      if('plan' in data) setVaPlan({"path":data.plan.path,"graph":data.plan.graph})
      if('plan' in data && 'views' in data.plan) {
        var tempView = data.plan.views;
        console.log(tempView)
        tempView.map((view, index) => {
          if(!('fields' in view)){
            view['fields']  = [""]
          }
          if(view['interactions'].length === 0){
            view['interactions'] = [{"verb":"","object":"","effect":{"description":""}}]
          }
          else {
            view['interactions'].map((interaction, index) => {
              if(!('params' in interaction)){
                interaction['params'] = [{"name":"","select":{}}]
              }
              if(typeof(interaction['effect']) === 'string'){
                interaction['effect'] = {"description":interaction['effect']}
              }
            })
          }
        })
        console.log(tempView)
        setViews(tempView)
        forceUpdate()
        console.log(views)
      }
        if('sqls' in data) setSqls(data.sqls)
        if('vlcodes' in data) setVlcodes(data.vlcodes)
  }

  const getVa = async () => {
    var JsonResult;
    console.log("!")
    try {
      // 使用await等待fetch完成
      const response = await fetch(`http://127.0.0.1:8888/api/vas?id=${openedVa.id}`, {
          method: 'GET',
          mode: 'cors',
      });
  
      if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
      }
  
      // 等待response.text()转换为文本，然后解析为JSON
      const resultText = await response.text();
      JsonResult = JSON.parse(resultText);
      console.log("JsonResult:", JsonResult); // 这里应该能正常打印出结果
  
  } catch (error) {
      console.error('请求或解析过程中发生错误:', error);
  }
    console.log(JsonResult)
    if(JsonResult!==undefined && JsonResult.message === "获取系统详情成功"){
      upDateVA(JsonResult.data)
      console.log("yes")
      setOpened(true)
    }
  }

  const Stages = ["DB Understanding","Requirements","Tasks","Plan","SQL","Vega-Lite","Vega-Lite"]
  const result_generate = async (stage)=>{
    var JsonData = {"id":openedVa.id,"desc":desc,"goal":goal,"initialStage":stage,"maxSteps":step,"useReflect":true,
            "useRag": true}
    if(stage > 0){
      JsonData.dataset = {"description":dbDescription,"tables":openedVaDetail};
    }
    if(stage > 1){
      console.log(designRequirements)
      JsonData.requirements = designRequirements;
    }
    if(stage > 2){
      var taskList = [];
      tasks.map((task, index) => {
        taskList.push({"type":task["Category"],"method":task["method"],"data":task["Data"],"priority":task["priority"],"taskId":task["id"], "objective":""})
    })
      JsonData.tasks = taskList;
    }
    if(stage > 3){
      JsonData.plan = {"graph":vaPlan.graph,"path":vaPlan.path,"views":views}
    }
    if(stage > 4){
      JsonData.sqls = sqls; 
    }
    if(stage > 5){
      JsonData.vlcodes = vlcodes;
    }
    if(stage === 10){
      JsonData.name = openedVa.name;
      console.log(JsonData)
      const response = await fetch(`http://127.0.0.1:8888/api/save`,{
        method:'POST',
        mode:'cors',
        body: JSON.stringify(JsonData),
        headers: {
          "Content-Type": "application/json", // ✅ 确保指定 JSON 类型
        },
      })
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    // 等待response.text()转换为文本，然后解析为JSON
    const resultText = await response.text();
    var JsonResult = JSON.parse(resultText);
    console.log("JsonResult:", JsonResult); // 这里应该能正常打印出结果
      return ;
    }
    setUpdate(true)
    var temp_log = []
    temp_log.push({"Stage":Stages[0],"status":"loading","Raw":""})
    setLogs(temp_log)
    forceUpdate()
    console.log(JsonData)
    
    const response = await fetch(`http://127.0.0.1:8888/api/generate`,{
      method:'POST',
      mode:'cors',
      body: JSON.stringify(JsonData),
      headers: {
        "Content-Type": "application/json", // ✅ 确保指定 JSON 类型
      },
    })
    console.log(response)
    const reader = response.body.getReader();
    const decoder = new TextDecoder("utf-8");

    let result = "";
    var value= await reader.read();
    if(value.done) return;

    while (update) {

      result = decoder.decode(value.value, { stream: true });
      console.log("Received chunk:", result); // 处理流数据
      let receivedChunk;
try {
    receivedChunk = JSON.parse(result);
} catch (error) {
    console.error('Error parsing input text:', error);
    throw error; // 或者根据需要处理错误
}

// 第二步：从receivedChunk的raw字段中提取并清理JSON内容
let rawJsonString = receivedChunk.raw;

// 打印原始的rawJsonString以便调试
console.log("Original rawJsonString:", rawJsonString);
if(rawJsonString === undefined) {
  continue;
}
// 去除开头和结尾的```json和```标记
if (typeof rawJsonString === 'string' && rawJsonString.startsWith("```json\n")) {
    rawJsonString = rawJsonString.substring(8).trim(); // 去掉开头的```json
}
if (rawJsonString.endsWith("```")) {
    rawJsonString = rawJsonString.slice(0, -3).trim(); // 去掉末尾的```
}

// 再次打印清理后的rawJsonString以便确认
console.log("Cleaned rawJsonString:", rawJsonString);

// 替换所有双反斜杠为单反斜杠，以修复可能的转义字符问题
rawJsonString = rawJsonString.replace(/\\\\/g, "\\");

// 第三步：解析提取出的JSON字符串
var parsedData ;
let data;
try {
    parsedData = JSON.parse(rawJsonString);
} catch (error) {
    console.error('Error parsing extracted JSON string:', error);
    console.error('Failed to parse:', rawJsonString); // 打印失败解析的字符串
    throw error; // 或者根据需要处理错误
}
  const stageName = parsedData.stage;
  const stageId = parsedData.stageId;
  const status = parsedData.go_ahead;
  const go_ahead = parsedData.go_ahead;
  upDateVA(parsedData.outputs)
    temp_log[temp_log.length-1].status = "done"
    temp_log[temp_log.length-1].Stage = Stages[stageId]
    value = await reader.read();
    setLogs(temp_log)
    forceUpdate()
    if(value.done)break;
    temp_log.push({"Stage":Stages[stageId+1],"status":"loading","Raw":""})
    setLogs(temp_log)
    forceUpdate()
    if(!go_ahead) break;
}
    getVa()
  }

 const [opened, setOpened] = useState(false);
  useEffect(()=>{
    
    console.log(openedVa)
    if(openedVa!=null) {Initial();getVa();  }
    if(opened){
      vegaEmbed("#vlchart", vlcodes);
    }
    console.log(views)
    console.log(designRequirements)
  },[openedVa])

  const [show, setShow] = useState(false);

  const handleClose = () => setShow(false);
  const handleShow = () => setShow(true);

  return (
    <div className="opened-va-panel">
      {opened ? (
        <div className="opened-va-content">
          {show && (
        <div className="modal-overlay">
          <div className="modal-content">
            <div className="modal-header">
              <h5 className="modal-title">Add Data</h5>
              <button className="close-btn" onClick={handleClose}>
                &times;
              </button>
            </div>
            <div className="modal-body">
            <div className="table-list" style = {{ "z-index":"999", "margin-bottom":"-200px", "background":"#white"}}>
                {openedVaDetail.map((item, index)=> {
                  return (
                  <div className="table-detail" style = {{"margin-left":"30px"}}>
                  <div className="table-item">
                    <Calendar className="calendar"/>
                    <div className="table-item-word">{item.table}</div>
                    <button onClick={()=>(listDetail(index))} className="list-button"><ListButton/></button>
                  </div>
                  {listedDetail[index] ? (<div className="table-item-list">{item.columns.map((item2)=>{
                      return (
                        <div className="table-item-list-word" onClick = {()=>{var temp = tasks;temp[taskChosen]["Data"].push(item.table+"."+item2.column);setTasks(temp);setAddData(!addData);forceUpdate()}}>
                          <div className="table-item-list-word-column">{item2.column}</div>
                          <div className="table-item-list-word-dtype">{item2.dtype}</div>
                        </div>
                      )
                    })}</div>) : (<div></div>) }
                  </div>  
                  )
                })}
              </div>
            </div>
            <div className="modal-footer">
              <button className="btn btn-secondary" onClick={handleClose}>
                关闭
              </button>
              <button className="btn btn-primary" onClick={handleClose}>
                保存更改
              </button>
            </div>
          </div>
        </div>
      )}
          {/* 栏1: 两个带标题的文本框 */}

          <div className="section section-1">
            <div className="opened-va-title-card">
              <Pipeline/>
              <div className="opened-va-title-text">Generation Pipeline</div>
            </div>

            <div className="logo-title">
              <Database/>
              <div className="logo-title-text">Database</div>
            </div>

            <Uploader action="http://127.0.0.1:5050/databse" // 后端上传接口地址
              onSuccess={handleFileUpload} // 成功回调函数
              onError={(response) => {
                setUploadStatus('Failed to upload the file.');
              }}
              onUpload={(_, file) => {
                setUploadStatus(`Uploading ${file.name}`);
              }}
              autoUpload={false} // 手动控制上传
              accept="*/*" 
              listType="text" // 防止 UI 组件自动渲染
              fileListVisible={false} // 隐藏文件列表
              showuploadList={false}
              className="upload-database">
              <div className="upload-database-button">Upload Database</div>
            </Uploader>
            <input 
              type="file" 
              id="customFileInput" 
              style={{ display: 'none' }} 
              onChange={handleFileChange} 
            />
            <div className="upload-database-button-fake" onClick={openFileDialog}>+ Upload Database</div>

            <div className="Input-Goal">
              <div className="Input-Title" >Analysis Goal</div>
                <textarea value = {goal} onChange = {goalInput}  style={{"background-color": "#F9F9F9", "color": "#333333",  "font-size": "12px", "fontFamily":"inter",}} className="textInput goalInput"/>
            </div>

            <div className="Input-Desc">
              <div className="Input-Title">Database Description</div>

                <textarea value = {desc} onChange = {descInput} style={{"background-color": "#F9F9F9", "color": "#333333",  "font-size": "12px", "fontFamily":"inter"}} className="textInput descInput"/>
            </div>

            <div className="Table-list">
              <div className="Input-Title light" onClick = {openVaDetail}>Original Tables({openedVaDetail.length})</div>
              {listVaDetail?<div className="table-list">
                {openedVaDetail.map((item, index)=> {
                  return (
                  <div className="table-detail">
                  <div className="table-item">
                    <Calendar className="calendar"/>
                    <div className="table-item-word">{item.table}</div>
                    <button onClick={()=>(listDetail(index))} className="list-button"><ListButton/></button>
                  </div>
                  {listedDetail[index] ? (<div className="table-item-list">{item.columns.map((item)=>{
                      return (
                        <div className="table-item-list-word">
                          <div className="table-item-list-word-column">{item.column}</div>
                          <div className="table-item-list-word-dtype">{item.dtype}</div>
                        </div>
                      )
                    })}</div>) : (<div></div>) }
                  </div>  
                  )
                })}
              </div>:<div/>}
            </div>
              <div className="Table-list2">
                <div className="Input-Title light" onClick = {openInter}> Intermediate Tables({intermediateTable.data.length})</div>
                {listInter ? <div className="table-list list2">
                  {intermediateTable.data.map((item, index)=> {
                    return (
                    <div className="table-detail">
                    <div className="table-item">
                      <Calendar className="calendar"/>
                      <div className="table-item-word">item.table</div>
                      <button onClick={()=>(listDetailI(index))} className="list-button"><ListButton/></button>
                    </div>
                    {listedDetailI[index] ? (<div className="table-item-list">{item.columns.map((item)=>{
                      return (
                        <div className="table-item-list-word">
                          <div className="table-item-list-word-column">{item.column}</div>
                          <div className="table-item-list-word-dtype">{item.dtype}</div>
                        </div>
                      )
                    })}</div>) : (<div></div>) }
                  </div>
                  )
                  })}
                </div> : <div/>}
              </div> 
          </div>
          <div className="section section-5">
            <div className="logo-title">
                <DesignRequirement/>
                <div className="logo-title-text">Design Requirements</div>
            </div>  
            <div className="Design-Requirements-Choice">
              <button className="Design-Requirements-List" onClick={()=>chooceRequirement("data")}>
                  {designRequirementsChosen === "data" ? <div className="up-shadow"/> : <div className="no-shadow"/>}
                  <DataRequirements className="Design-Requirements-List-Icon"/>
              </button>
              <button className="Design-Requirements-List" onClick={()=>chooceRequirement("visualization")}>
                  {designRequirementsChosen === "visualization" ? <div className="up-shadow"/> : <div className="no-shadow"/>}
                  <VisRequirements className="Design-Requirements-List-Icon"/>
              </button>
              <button className="Design-Requirements-List" onClick={()=>chooceRequirement("interaction")}>
                  {designRequirementsChosen === "interaction" ? <div className="up-shadow"/> : <div className="no-shadow"/>}
                  <IntRequirements className="Design-Requirements-List-Icon"/>
              </button>
            </div>
            <div className="Design-Requirements-list">
            {
              designRequirements[designRequirementsChosen].map((item, index)=>{
                return (
                  <div className="Design-Requirements-List-Item" >
                    <div className="Design-Requirements-List-Item-Title">{index+1}</div>
        
                    <textarea style={{"background-color": "#F9F9F9", "color": "#333333",  "font-size": "12px", "fontFamily":"inter"}} className="Design-Requirements-List-Item-Description" value = {item['requirement']} onChange = {(e)=>{var temp = designRequirements;temp[designRequirementsChosen][index]['requirement'] = e.target.value;setDesignRequirements(temp);forceUpdate()}}></textarea>
                    
                    <Delete className="Design-Requirements-List-Item-Delete" onClick={()=>deleteRequirement(index)}/>
                  </div>
                )
              })
            }
            </div>
            <button className="Add-Design-Requirements" onClick = {()=>{var temp = designRequirements;temp[designRequirementsChosen][designRequirements[designRequirementsChosen].length]= {"requirement":designRequirementsChosen.charAt(0).toUpperCase() + designRequirements[designRequirementsChosen].length.toString(),"Id":designRequirements.length+1,"reason":""};console.log(temp);setDesignRequirements(temp);forceUpdate()}}>+Add</button>
          </div>
          <div className="section section-new">
            <div className="logo-title Analy">
              <Analy/>
              <AnalyTick className="combine-tick"/>
              <div className="logo-title-text">Analytical Tasks</div>
            </div>   
            <div className="Task-control">
            {tasks.map((item, index)=>{

              return (<div className="Task-box" style = {{background:index !== taskChosen ? "#F3F3F3" : "#D3D3D3"}} onClick = {()=>setTaskChosen(index)}>
                <div className="Task-box-num" >{index+1}</div>
              </div>)
            })}
              <div className="task_underline"></div>
            </div>
            <div className="word-window Category-word-window">
              <div className="word-window-word ">Category</div>
              <select className="Category-window" value ={ tasks[taskChosen]["Category"]}  onChange ={(e)=> {var temp = tasks;temp[taskChosen]["Category"] = e.target.value;setTasks(temp);console.log(tasks);forceUpdate()}}>
              {categoryList.map((item, index)=>{
                    return (<option className="Category-list-item" value={item}>{item}</option>)
                })}
              </select>

            </div>
            <div className="word-window">
              <div className="word-window-word Data-word">Data</div>
              <div className="word-window-window Data-window">{tasks[taskChosen]["Data"].map((item, index)=>{
                return (<div className="data-note"><div className="data-item">{item}</div>< DeleteCross className="DeleteCross" onClick = {()=>deleteData(index)}/></div>)
              })}
              <div className="data-note-add" onClick = {handleShow}>+</div>
              
              </div>
              </div>
              

              <div className="word-window">
              <div className="word-window-word Method-word">Method</div>
              <textarea style={{"background-color": "#F3F3F3", "color": "#333333", "font-size": "12px", "fontFamily":"inter"}}className="word-window-window Method-window" value = {tasks[taskChosen]["method"]} onChange = {(e)=>{var temp = tasks;temp[taskChosen]["method"] = e.target.value;setTasks(temp);forceUpdate()}}></textarea>
              
            </div>
            <div className="word-window">
              <div className="word-window-word Priority-word">Priority</div>
              <div className="word-window-minus" onClick = {minusPriority}>-</div>
              <div className="word-window-window Priority-window">{tasks[taskChosen]["priority"]}</div>
              <div className="word-window-plus" onClick = {addPriority}>+</div>
            </div>
            <div className="logo-title Analy">
              <AnalyPlan/>
              <div className="logo-title-text">Analytical Plan</div>
            </div>   
            <div className="word-window">
              <div className="word-window-word Plan-word">Overall Plan</div>
              <textarea style={{"background-color": "#F3F3F3", "color": "#333333",  "font-size": "12px", "fontFamily":"inter"}}className="word-window-window Plan-window" value = {vaPlan.path} onChange = {(e)=>{var temp = vaPlan;temp['path'] = e.target.value;setVaPlan(temp)}}></textarea>
            </div>
            <div className="Task-control">
            {views.map((item, index)=>{
              return (<div className="Task-box" style = {{background:index !== viewChosen ? "#F3F3F3" : "#D3D3D3"}} onClick = {()=>setViewChosen(index)}>
                <div className="Task-box-num" >{index+1}</div>
              </div>)
            })}
              <div className="task_underline"></div>
            </div>
            <div className="word-window Category-word-window">
              <div className="word-window-word">Level</div>
              
              <select className="Category-window Level-window" value ={ views[viewChosen]["level"]}  onChange ={(e)=> {var temp = views;temp[viewChosen]["level"] = e.target.value;setViews(temp);console.log(tasks);forceUpdate()}}>
              {levelList.map((item, index)=>{
                    return (<option className="Category-list-item" value={item}>{item}</option>)
                })}
              </select>
            </div>
            <div className="word-window">
              <div className="word-window-word Vis-word">Visualization</div>
               <textarea style={{"background-color": "#F3F3F3", "color": "#333333",  "font-size": "12px", "fontFamily":"inter"}}className="word-window-window Vis-window" value = {views[viewChosen]["visualization"]['description']} onChange = {(e)=>{var temp = views;temp[viewChosen]["visualization"]['description'] = e.target.value;setViews(temp);forceUpdate()}}></textarea>
            </div>
                        
            <div className="Interaction-window">
                <div className="Interaction-word">Interactions    ({InteractionChosen+1} of {views[viewChosen]['interactions'].length})</div>
                <div className={InteractionChosen>0 ? "ltri-black" : "ltri"} onClick = {()=>{if(InteractionChosen>0 ){setInteractionChosen(InteractionChosen - 1)}}}></div>
                <div className="Interaction-word-window">
                  <textarea style={{"background-color": "#F3F3F3", "color": "#333333",  "font-size": "12px", "fontFamily":"inter"}}className="Interaction-action" value = {views[viewChosen]['interactions'][InteractionChosen]["verb"]} onChange = {(e)=>{var temp = views;temp[viewChosen]["Interactions"][InteractionChosen]["verb"] = e.target.value;setViews(temp);forceUpdate()} }></textarea>
                  <div className="Interaction-on">on</div>
                    <textarea style={{"background-color": "#F3F3F3", "color": "#333333",  "font-size": "12px", "fontFamily":"inter"}}className="Interaction-position textarea-position" value = {views[viewChosen]["interactions"][InteractionChosen]["object"]} onChange = {(e)=>{var temp = views;temp[viewChosen]["interactions"][InteractionChosen]["object"] = e.target.value;setViews(temp);;forceUpdate()}}></textarea>
                  <div className="Interaction-then">then</div>
                    <textarea style={{"background-color": "#F3F3F3", "color": "#333333",  "font-size": "12px", "fontFamily":"inter"}}className="Interaction-response" value = {views[viewChosen]["interactions"][InteractionChosen]["effect"]["description"]} onChange = {(e)=>{var temp = views;temp[viewChosen]["interactions"][InteractionChosen]["effect"]["description"] = e.target.value;setViews(temp);;forceUpdate()}}></textarea>
                </div>
                <div className={InteractionChosen < views[viewChosen]["interactions"].length-1 ? "rtri-black":"rtri"} onClick = {()=>{if(InteractionChosen < views[viewChosen]["interactions"].length-1 ){setInteractionChosen(InteractionChosen + 1)}}}></div>
            </div>
            <div className="word-window Source-word-window">
              <div className="word-window-word">Source</div>
              
              <textarea style={{"background-color": "#F3F3F3", "color": "#333333",  "font-size": "12px", "fontFamily":"inter"}}className="word-window-window Source-window" value = {views[viewChosen]['fields'].join(',')} onChange = {(e)=>{var temp = views;views[viewChosen]['fields'] = (e.target.value).slplit(',');setViews(temp);;forceUpdate()}}></textarea>
            </div>
          </div>     
          <div className="section section-3">
            <div id="vlchart" className="vlgraph"></div>
            <Refresh className="refresh" onClick = {()=>{vegaEmbed("#vlchart", vlcodes)}}/>
            <Unfold className="unfold" onClick = {()=>{setShowCode(!showCode); setCode0(JSON.stringify(vlcodes))}}/>
            <div className="codeText" style = {{"display":showCode ? "block":"none",}}>
              <div style = {{"transform":"scale(2)"}} className="closeCode">
              <DeleteCross  onClick = {()=>{setShowCode(!showCode)}}/>
              </div>
              {code}
            </div>
          </div>
          <div className="section section-7">
            <div className="section section-l">
              <div className="opened-va-title-card">
                <PipelinePanel/>
                <div className="opened-va-title-text">Control Panel</div>
              </div>
              <div className="pipeline-control">
                <div className="pipeline-circ" onClick = {()=>{setStage(1)}} style = {{"background-color":stage === 1 ?"#445CDD":stage > 1 ? "#9FA8DA":"#D9D9D9"}}>1</div>
                <UpTri style = {{"margin-left":"-22px", "margin-top":"40px", "opacity":stage === 1 ? "100%":"0"}}/>
                <div className="pipeline-line"></div>
                <div className="pipeline-circ" onClick = {()=>{setStage(2)}} style = {{"background-color":stage === 2 ?"#445CDD":stage > 2 ? "#9FA8DA":"#D9D9D9"}}>2</div>
                <UpTri style = {{"margin-left":"-22px", "margin-top":"40px", "opacity":stage === 2 ? "100%":"0"}}/>
                <div className="pipeline-line"></div>
                <div className="pipeline-circ" onClick = {()=>{setStage(3)}} style = {{"background-color":stage === 3 ?"#445CDD":stage > 3 ? "#9FA8DA":"#D9D9D9"}}>3</div>
                <UpTri style = {{"margin-left":"-22px", "margin-top":"40px", "opacity":stage === 3 ? "100%":"0"}}/>
                <div className="pipeline-line"></div>
                <div className="pipeline-circ" onClick = {()=>{setStage(4)}} style = {{"background-color":stage === 4 ?"#445CDD":stage > 4 ? "#9FA8DA":"#D9D9D9"}}>4</div>
                <UpTri style = {{"margin-left":"-22px", "margin-top":"40px", "opacity":stage === 4 ? "100%":"0"}}/>
                <div className="pipeline-line"></div>
                <div className="pipeline-circ" onClick = {()=>{setStage(5)}} style = {{"background-color":stage === 5 ?"#445CDD":stage > 5 ? "#9FA8DA":"#D9D9D9"}}>5</div>
                <UpTri style = {{"margin-left":"-22px", "margin-top":"40px", "opacity":stage === 5 ? "100%":"0"}}/>
                <div className="pipeline-line"></div>
                <div className="pipeline-circ" onClick = {()=>{setStage(6)}} style = {{"background-color":stage === 6 ?"#445CDD":stage > 6 ? "#9FA8DA":"#D9D9D9"}}>6</div>
                <UpTri style = {{"margin-left":"-22px", "margin-top":"40px", "opacity":stage === 6 ? "100%":"0"}}/>
              </div>
              <div className="word-window MAx-step">
              <div className="word-window-word Priority-word">Max Steps</div>
              <div className="word-window-minus Pipeline-minus" onClick = {()=>{console.log(step);if(step > 1) {setStep(step-1);forceUpdate()}}}>-</div>
              <div className="word-window-window Pipeline-window">{step}</div>
              <div className="word-window-plus" onClick = {()=>{console.log(step);if(step < 999){ setStep(step+1);forceUpdate()}}}>+</div>
              <div style = {{"margin-left": "-200px"}}>
              <div className="button-1" onClick = {()=>{setLogs([]);result_generate(0)}}>Start From Beginning</div>
              <div className="button-2" onClick = {()=>{setLogs([]);result_generate(10)}}>Save Draft</div>
              <div className="button-3" onClick = {()=>{setLogs([]);result_generate(stage-1)}}>Start From Stage {stage}</div>
              <div className="button-4" onClick = {()=>{setUpdate(false)}}>Stop</div>
              </div>
            </div>
            </div>
            <div className="section section-r">
              <div className="opened-va-title-card">
                <Logs/>
                <div className="opened-va-title-text">Logs</div>
              </div>
              <div className="log-titles">
                Step&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
                Stage&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
                Status&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
                Detail
              </div>
              <div style = {{"width":"330px","height":"1px","background-color":"#333333", "margin-left":"10px","margin-top":"6px"}}/>
              <div className="log-list">
              {logs.map((log, index) => {
                return (<div className="log-item">
                  <div className="log-Step">{index+1}</div>
                  <div className="log-Stage">{log.Stage}</div>
                  <div className="log-status">{log.status === "loading" ? <Loading/> : log.status === "warning" ? <Warning/>:<GreenTick/>}</div>
                  <div className="log-Detail" style={{"color":log.status === "loading" ? "#C1C1C1" : "#1296DB"}} onClick = {()=>{if(log.status !== "loading") {setShowCode(!showCode);setCode0(log.Raw);}}}>View Raw</div>
                </div>)
              })}
              </div>
            </div>
          </div>
          {/* 栏4: 分为左右两栏 */}
          {/*<div className="section section-4">
            <div className="top">
              <div className="opened-va-title-card">
                <Plan/>
                <div className="opened-va-title-text">Analysis Plan</div>
              </div>
              <button className="black-butom" onClick={()=>generatePlan(openedVa)}>Generate Plan</button>
              <button className="black-butom" onClick={()=>generateVegaLite(openedVa)}>Generate Vega-lite</button>
            </div>
            <div className="split">
              <div className="left">
                <div className="Input-ViewTitle">
                  <div className="Input-Title">View Title</div>
                  {viewTitleEdit?
                    <textarea onChange = {viewTitleInput} className="textInput viewTitleInput"/> : 
                    <div id="text2" style = {{'max-length':"2"}} className="textInput viewTitleInput">{viewTitle.length > 160 ? viewTitle.slice(0,160) + ' · · · ' : viewTitle}</div>}
                  <EditNote className="editName"  onClick = {onViewTitleInput}/>
                </div>
                <div className="Input-Vis">
                  <div className="Input-Title">Visualization</div>
                  {visEdit?
                    <textarea onChange = {VisInput} className="textInput visInput"/> : 
                    <div id="text2"  style = {{'max-length':"2"}}className="textInput visInput">{vis.length > 160 ? vis.slice(0,160) + ' · · · ' : vis}</div>}
                  <EditNote className="editName"  onClick = {onVisInput}/>
                </div>
              </div>
              <div className="right">
                <div className="Input-DataSource">
                  <div className="Input-Title">Data Source</div>
                  {dsEdit?
                    <textarea onChange = {dsInput} className="textInput dataSourceInput"/> : 
                    <div id="text2"  style = {{'max-length':"2"}}className="textInput dataSourceInput">{ds.length > 160 ? desc.slice(0,160) + ' · · · ' : ds}</div>}
                  <EditNote className="editName"  onClick = {onDsInput}/>
                </div>
                <div className="Input-IntAndCor">
                  <div className="Input-Title">Interaction & coordianation</div>
                  {intAndCorEdit?
                    <textarea onChange = {intAndCorInput} className="textInput intAndCorInput"/> : 
                    <div id="text2"  style = {{'max-length':"2"}}className="textInput intAndCorInput">{intAndCor.length > 160 ? intAndCor.slice(0,160) + ' · · · ' : intAndCor}</div>}
                  <EditNote className="editName"  onClick = {onIntAndCorInput}/>
                </div>
              </div>
            </div>
          </div>
          <div className="section section-56">
          </div>*/}

          {/* 栏6: 类似 ChatGPT 的聊天视图 */}
          {/*<div className="section section-6">
          <div className="opened-va-title-card">
            <Chat/>
              <div className="opened-va-title-text">Chat View</div>
            </div>
            <div className="chat-view">
              <div className="messages">
                <div className="message">
                  <strong>User:</strong> Hello!
                </div>
                <div className="message">
                  <strong>VA:</strong> Hi there! How can I assist you today?
                </div>
              </div>
              <div className="input-area">
                <input type="text" placeholder="Type your message here..." />
                <button>Send</button>
              </div>
            </div>
          </div>*/}
        </div>
      ) : (
        <p>No VA opened</p>
      )}
    </div>
  );
};

export default OpenedVaPanel;