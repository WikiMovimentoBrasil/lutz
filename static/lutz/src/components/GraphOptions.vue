<template>
      <v-autocomplete
        v-if="loaded" 
        v-model="select"
        :loading="loading"
        :items="wikis"
        density="comfortable"
        hide-no-data
        hide-details
        label="wiki"
        @update:model-value="this.$emit('changedWiki', this.select)"
      ></v-autocomplete>
  </template>
<script lang="ts">
const host = 'https://lutz.toolforge.org/'
export default {
  data () {
    return {
        loaded: false,
      loading: false,
      items: [ 'ptwiki'],
      select: 'ptwiki',
      wikis: [ 'ptwiki']
    }
  },
  async mounted () {
        this.loaded = false
        try {
            const wikis = await fetch(`${host}/wikis`)
            this.wikis = await wikis.json()
            this.loaded = true
        } catch (e) {
    console.error(e)
        }
    },
}
</script>
