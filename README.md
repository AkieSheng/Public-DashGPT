# DashGPT

## 项目简介
项目基于 Flask 和 Vue 开发了一个端到端系统，输入多张数据表格和用户分析目标，即可全自动生成具有交互协调能力的多视图可视化仪表板。
系统基于大语言模型，自动完成从数据分析、图表设计到代码生成的全流程，并通过Web界面实时反馈进度和结果。

## 项目启动方法

### 启动后端

启动一个终端，进入 Rear 目录：
```sh
cd Rear
```

安装所需的依赖：
```sh
pip install flask flask-cors
```

启动服务器后端：
```sh
python web.py
```

(如果你的机器性能良好，你也可以同步运行两个后端进程，并行完成后端工作)
```sh
python web2.py
```

### 启动前端

启动另一个终端，进入 Front 目录：
```sh
cd Front
```


安装所需的依赖并启动：
```sh
npm install
npm start
```

浏览器访问 http://localhost:3000 即可进入网站

## 祝您使用愉快！！！