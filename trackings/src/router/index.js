import Vue from 'vue'
import VueRouter from 'vue-router'
import Home from '../views/Home.vue'
import PostSQL from '../views/PostSQL.vue'
Vue.use(VueRouter)

const routes = [
  {
    path: '/',
    name: 'PostSQL',
    component: PostSQL
  },
  {
    path: '/home',
    name: 'Home',
    component: Home
  },


]

const router = new VueRouter({
  routes
})

export default router
