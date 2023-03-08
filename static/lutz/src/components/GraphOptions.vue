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
        @update:model-value="emitChangedWiki"
      ></v-autocomplete>
      <v-select
        v-model="dataType"
        :items="dataTypes"
        :label="this.$t('message.dataType')"
        @update:model-value="this.$emit('changedDataType', this.dataType)"
      />
  </template>
<script lang="ts">
const host = 'https://lutz.toolforge.org/'
import type {DataType} from './GraphConfig.js'
export default {
  data () {
    return {
      loaded: false,
      loading: false,
      items: [ 'ptwiki'],
      select: 'ptwiki',
      wikis: [ 'ptwiki'],
      dataTypes: ['%_of_editors', 'count', 'editcount', '%_of_edits'],
      dataType: <DataType> '%_of_edits'
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
  methods:{
    emitChangedWiki: function(event: unknown){
      this.$emit('changedWiki', this.select)
    }
  }
}
</script>
