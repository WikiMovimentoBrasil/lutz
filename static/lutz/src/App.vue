<script setup lang="ts">
import { RouterLink, RouterView } from 'vue-router'
</script>
<script lang="ts">
 export default {
    data () {
      return {
        locales: this.$i18n.availableLocales,
      }
    },
  }</script>

<template>
  <header>
    <img alt="Bertha Lutz" class="logo" src="@/assets/bertha-removebg.png" width="60" height="60" />

      <nav>
        <RouterLink to="/">{{ $t("menu.home")}}</RouterLink>
        <RouterLink to="/about">{{ $t("menu.about")}}</RouterLink>
      </nav>
    <div class="wrapper-left">
      <div class="locale-changer">
        <v-select
          :items="locales"
          prepend-inner-icon="mdi-translate-variant"
          v-model="$i18n.locale"
          density="compact"
          :hide-details=true
        >
        </v-select>
      </div>
    </div>
    <div class="wrapper-right">
      <img alt="Logo negativo do Wiki Movimento Brasil" class="logo-wmb" src="https://upload.wikimedia.org/wikipedia/commons/8/82/Wiki_Movimento_Brasil_-_logo_negativo.svg" />
    </div>
  </header>

  <RouterView />
</template>

<style scoped>
header {
  line-height: 1.5;
  max-height: 100vh;
  min-height: 9vh;
}
nav {
  max-width: fit-content;
}

.locale-changer {
}
.logo-wmb {
  max-height: 8vh;
  position: absolute;
  margin-top: 0.5vh;
  right: 0;

}
.wrapper-right {
  display: block;
  position: absolute;
  right: 0;
  top: 0;
  margin: 0 auto 2rem;
  min-height: 5vh;
  min-width: 40vh;
}
.wrapper-left {
  position: relative;
  display: block;
  left: 0;
  }
.logo {
  display: block;
  margin: 0 2rem 0 0;
}

nav {
  width: 100%;
  font-size: 12px;
  text-align: center;
  margin-top: 2rem;
}

nav a.router-link-exact-active {
  color: var(--color-text);
}

nav a.router-link-exact-active:hover {
  background-color: transparent;
}

nav a {
  display: inline-block;
  padding: 0 1rem;
  border-left: 1px solid var(--color-border);
}

nav a:first-of-type {
  border: 0;
}

@media (min-width: 620px) {
  header {
    display: flex;
    place-items: center;
    padding-right: calc(var(--section-gap) / 2);
  }

  nav {
    text-align: left;
    margin-left: -1rem;
    font-size: 1rem;

    padding: 1rem 0;
    margin-top: 1rem;
  }
}
</style>
