import Vue from 'vue'
import ElementUI from 'element-ui';
import 'element-ui/lib/theme-chalk/index.css';
import App from './App.vue'
import router from './router'
import store from './store'
import axios from 'axios'
// import VConsole from 'vconsole'
// const vConsole = new VConsole()
// Vue.use(vConsole)
// console.info("vconsole-info-测试")
Vue.use(ElementUI);
Vue.prototype.axios= axios
Vue.config.productionTip = false
new Vue({
  router,
  store,
  render: h => h(App)
}).$mount('#app')
