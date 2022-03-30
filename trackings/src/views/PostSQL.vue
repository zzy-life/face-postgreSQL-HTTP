<template>
  <div class="testTracking">
    <video
      id="video"
      width="318"
      height="270"
      preload
      autoplay
      loop
      muted
      v-show="canvasis"
    ></video>
    <canvas id="canvas" width="318" height="270" v-show="canvasis"></canvas>
    <canvas
      id="screenshotCanvas"
      width="318"
      height="270"
      style="display: none"
    ></canvas>
    <div class="buttonDiv">
      <el-card class="box-card"> 请先打开摄像头注册，才可识别出姓名
         <el-divider></el-divider>
         移动端使用GPU计算需要5秒识别
         </el-card>

      <el-button
        type="success"
        icon="el-icon-check"
        @click="openCamera()"
        v-show="!canvasis && video == undefined"
        >打开摄像头</el-button
      >
      <el-button
        type="primary"
        icon="el-icon-edit"
        @click="offvideo()"
        v-show="canvasis"
        >关闭摄像头</el-button
      >
      <el-button
        type="primary"
        icon="el-icon-edit"
        @click="
          popup.open = true;
          popup.key = false;
        "
        v-show="canvasis && video != undefined"
        >拍照注册</el-button
      >
    </div>

    <el-dialog title="请输入您的信息" :visible.sync="popup.open" width="80%">
      <el-form ref="form" label-width="80px" :model="popup" :rules="rules">
        <el-form-item label="用户名" prop="username">
          <el-input v-model="popup.username"></el-input>
        </el-form-item>
        <el-form-item label="手机号" prop="phone">
          <el-input v-model="popup.phone"></el-input>
        </el-form-item>
        <el-form-item label="邮箱" prop="mail">
          <el-input v-model="popup.mail"></el-input>
        </el-form-item>
      </el-form>

      <span slot="footer" class="dialog-footer">
        <el-button @click="popup.open = false">取 消</el-button>
        <el-button
          v-show="popup.imgData != undefined"
          type="primary"
          @click="zhuce('form')"
          >确 定</el-button
        >
      </span>
    </el-dialog>
    <img :src="src" id="imgsrc" />
    <form
      id="form1"
      method="post"
      enctype="multipart/form-data"
      action=""
      style="display: none"
    >
      <input id="file" type="file" name="file" />
    </form>
  </div>
</template>

<script>
require("tracking/build/tracking-min.js");
require("tracking/build/data/face-min.js");
require("tracking/examples/assets/stats.min.js");

export default {
  name: "PostSQL",
  data() {
    return {
      src: undefined,
      recty: 0,
      rectx: 0,
      trackerTask: undefined,
      screenshotCanvas: null,
      video: undefined,
      canvasis: false,
      popup: {
        open: false, //弹窗
        username: undefined, //表单姓名
        phone: undefined, //表单手机
        mail: undefined, //表单邮件
        imgData: undefined, //表单人脸
        key: true, //表单注册人脸锁
      },
      rules: {
        username: [
          {
            required: true, //是否必填
            message: "用户名不能为空", //规则
            trigger: "blur", //何事件触发
          },
        ],
        phone: [
          {
            required: true, //是否必填
            message: "手机号不能为空", //规则
            trigger: "blur", //何事件触发
          },
        ],
        mail: [
          {
            required: true, //是否必填
            message: "邮箱不能为空", //规则
            trigger: "blur", //何事件触发
          },
        ],
      },
    };
  },
  mounted() {
    // this.axios({
    //   method: "get",
    //   url: "https://postgre-face-890657-1305567820.ap-shanghai.run.tcloudbase.com",
    //   // url: "http://192.168.0.106:5001/face/verification",
    // }).then((response) => {});
  },
  methods: {
    openCamera() {
      var video = document.getElementById("video");
      this.screenshotCanvas = document.getElementById("screenshotCanvas");
      this.video = video;
      navigator.mediaDevices
        .getUserMedia({ video: { facingMode: "user" } })
        .then(function (stream) {
          document.getElementById("video").srcObject = stream;
        })
        .catch(function (error) {
          alert(error);
        });
      var canvas = document.getElementById("canvas");
      var context = canvas.getContext("2d");
      var tracker = new tracking.ObjectTracker("face");
      tracker.setInitialScale(4);
      tracker.setStepSize(2);
      tracker.setEdgesDensity(0.1);

      this.trackerTask = tracking.track("#video", tracker, { camera: true });
      this.canvasis = true;
      let flag = true; //人脸锁
      let axiosflag = true; //接口锁
      let name = "识别中..";
      tracker.on("track", (event) => {
        if (event.data.length === 0) {
          //人脸变动，解锁
          flag = true;
          name = "识别中..";
        }

        context.clearRect(0, 0, canvas.width, canvas.height);
        event.data.forEach((rect) => {
          context.font = "20px Helvetica";
          context.fillText(name, rect.x + 20, rect.y - 40);

          context.strokeStyle = "#a64ceb";
          context.strokeRect(
            rect.x - 20,
            rect.y - 20,
            rect.width + 20,
            rect.height + 20
          );
        });
        if (event.data.length) {
          // 会不停的去检测人脸，所以这里需要做个锁
          if (flag && axiosflag) {
            flag = false;
            axiosflag = false;
            // 裁剪出人脸并绘制下来
            let canvasUpload = this.screenshotCanvas;
            let contextUpload = canvasUpload.getContext("2d");
            contextUpload.drawImage(
              video,
              0,
              0,
              canvasUpload.width,
              canvasUpload.height
            );
            // 人脸的basa64
            var image = this.saveAsPNG(canvasUpload);
            // this.src =  image;
            if (this.popup.key) {
              this.popup.imgData = image;
            }

            var formElement = document.getElementById("form1");
            var formData = new FormData(formElement);
            formData.set("file", this.dataURLtoFile(image, "aa.jpg"));
            if (
              /android|webos|iphone|ipod|balckberry/i.test(navigator.userAgent)
            ) {
              formData.set("type", "1");
            }
            this.axios({
              method: "post",
              // url: "https://postgre-face-890657-1305567820.ap-shanghai.run.tcloudbase.com/face/verification",
              url: "http://192.168.0.117:5001/face/verification",
              data: formData,
              headers: {
                "Content-Type": "multipart/form-data",
              },
            }).then((response) => {
              console.log(response);
              axiosflag = true;
              if (response.data.username) {
                name = response.data.username;
              }
            });
          }
        }
      });
    },
    zhuce(formName) {
      let imgData = this.popup.imgData;
      var formElement = document.getElementById("form1");
      var formData = new FormData(formElement);
      this.$refs[formName].validate((valid) => {
        if (valid) {
          formData.set("file", this.dataURLtoFile(imgData, "aa.jpg"));
          formData.append("mail", this.popup.mail);
          formData.append("username", this.popup.username);
          formData.append("phone", this.popup.phone);
          this.axios({
            method: "post",
            // url: "https://postgre-face-890657-1305567820.ap-shanghai.run.tcloudbase.com/face/registration",
            url: "http://192.168.0.117:5001/face/registration",
            data: formData,
            headers: {
              "Content-Type": "multipart/form-data",
            },
          }).then((response) => {
            console.log(response);
            if (response.data.code == "200") {
              this.$message({
                type: "success",
                message: "注册成功",
              });
            } else {
              this.$message({
                type: "error",
                message: response.data.face_encodings,
              });
            }
            this.popup.open = false;
            this.popup.key = true;
          });
        } else {
          return false;
        }
      });
    },

    dataURLtoFile(dataurl, filename) {
      var arr = dataurl.split(","),
        mime = arr[0].match(/:(.*?);/)[1],
        bstr = atob(arr[1]),
        n = bstr.length,
        u8arr = new Uint8Array(n);
      while (n--) {
        u8arr[n] = bstr.charCodeAt(n);
      }
      var file = new File([u8arr], filename, { type: mime });
      return file;
    },

    // 保存为png,base64格式图片
    saveAsPNG(c) {
      return c.toDataURL("image/jpeg");
    },
    offvideo() {
      // 停止侦测
      this.trackerTask.stop();
      // 关闭摄像头
      this.video.pause();
      this.video.srcObject.getVideoTracks()[0].stop();
      this.canvasis = false;
    },
  },
};
</script>
<style lang="less" scoped>
.testTracking {
  height: 100vh;
  width: 100%;
  position: relative;
  > * {
    position: absolute;
    left: 0;
    right: 0;
    margin: auto;
  }
  video,
  canvas {
    top: 0;
  }
  .box-card {
    margin-bottom: 31px;
  }
  .buttonDiv {
    bottom: 65px;
  }
}
</style>
