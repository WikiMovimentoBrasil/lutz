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
      <v-text-field
        type="date"
        :label="this.$t('message.startDate')"
        :value="this.after"
        @input="event => after = event.target.value"
        @update:model-value="emitChangedStartDate"
        emits="changedStartdate"
      ></v-text-field>

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
      dataType: <DataType> '%_of_edits',
      after: <Date | string > new Date(new Date().setDate(new Date().getDate() - 30))
    }
  },
  async mounted () {
        this.loaded = false
        try {
            const wikis = await fetch(`${host}/wikis`)
            this.after = this.after.toISOString().split('T')[0]
            this.wikis = await wikis.json()
            this.loaded = true
        } catch (e) {
    console.error(e)
        }
    },
  methods:{
    emitChangedWiki: function(event: unknown){
      this.$emit('changedWiki', this.select)
    },
    emitChangedStartDate: function(event: unknown){
      this.$emit('changedStartDate', event)
    }
  }
}
</script>
