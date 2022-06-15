# graduation-projects
2018 graduation projects

基于FU740的在线实验平台

  在本项工作中，主要研究对FU740的控制以及建立一个线上实验平台。

  通过复现前人工作，一步一步透过自己的方法在新的树莓派上搭建自己的服务器。在这过程中作出了改进方案，如增加机器使用额、脚本获取动态IP、增加交换机。在执行改进方案之后，开始了平台的设计构思，设计出服务器的框架，包括以Moodle作基础，搭建数据库，使用Docker作资源调度，预约机器分配策略。

  最终对U740的控制达到了以下五项：GPIO电源控制、HDMI的输出、TFTP文件传输、OpenOCD调试U-Boot以及JTAG串口读取；线上平台提供交互界面并支持申请预约功能；服务器端实现预约优先分配算法以及机器状态更新算法。整合后成功实现了一个基于FU740，利用Moodle作前端的线上交互平台。

相关信息：

- [选题过程](https://shimo.im/docs/ckyvdTXk3dD9ycrk?accessToken=eyJhbGciOiJIUzI1NiIsImtpZCI6ImRlZmF1bHQiLCJ0eXAiOiJKV1QifQ.eyJhdWQiOiJhY2Nlc3NfcmVzb3VyY2UiLCJleHAiOjE2NTUyNzQxODAsImZpbGVHVUlEIjoiSjlrV0pSallWeXFodkp5RCIsImlhdCI6MTY1NTI3Mzg4MCwidXNlcklkIjoxNTk4Njg4Nn0.ZfNJKcYFNOET-fqtZ_J5aYvWalZHuLnYCBOkWC5t0xs)
- [开题报告](https://github.com/nubbi3/graduation-projects/blob/2022-06-15/PPT/30%E8%99%9F%E7%AD%94%E8%BE%AFppt(%E6%9B%B4%E6%96%B0%E7%89%882).pptx)
- [中期报告](https://github.com/nubbi3/graduation-projects/blob/2022-06-15/PPT/6%E8%99%9F%E4%B8%AD%E6%9C%9F%E7%AD%94%E8%BE%AF(%E6%9B%B4%E6%96%B0%E7%89%88).pptx)
- [答辩报告](https://github.com/nubbi3/graduation-projects/blob/2022-06-15/PPT/8%E8%99%9F%E7%AD%94%E8%BE%AF.pptx)
- [在线论文](https://github.com/nubbi3/graduation-projects/blob/2022-06-15/Doc/%E5%9F%BA%E4%BA%8EFU740%E7%9A%84%E7%BA%BF%E4%B8%8A%E7%A1%AC%E4%BB%B6%E4%BA%A4%E4%BA%92%E5%AE%9E%E9%AA%8C%E5%B9%B3%E5%8F%B0%E5%BC%80%E5%8F%91.pdf)
- [代码仓库](https://github.com/nubbi3/graduation-projects/tree/2022-06-15/src)
- [在线搭建手册](https://github.com/nubbi3/graduation-projects/blob/2022-06-15/Log/FU740%E7%B7%9A%E4%B8%8A%E7%B3%BB%E7%B5%B1%E6%90%AD%E5%BB%BA%E6%96%87%E6%AA%94.pdf)
- [在线协调手冊](https://shimo.im/docs/rp3OVRG4Wdu9zzAm/)
