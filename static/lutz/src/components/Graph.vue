<template>
    <GraphOptions
        @changedWiki="changedWiki"
        @changedDataType="changedDataType"
        @changedStartDate="changedStartDate"
    > </GraphOptions>
    <div class="chart-container" style="position: relative; height:78vh; width:100vw">
  <Line v-if="loaded" :data="data" ref="line" style="{maintainAspectRatio: false, aspectRatio:1/10}"/>
  <div v-else> {{$t("message.loading")}}</div>
    </div>
</template>

<script lang="ts">
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Colors
} from 'chart.js'
import { Line } from 'vue-chartjs'
import * as chartConfig from './GraphConfig.js'
import type {DataType} from './GraphConfig.js'
import GraphOptions from './GraphOptions.vue'

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Colors
)

const host = 'https://lutz.toolforge.org/'

export default {
    name: 'Graph',
    components: {
        Line,
        GraphOptions
    },
    data: () => ({
        loaded: false,
        wiki: 'ptwiki',
        dataType: <DataType> "%_of_edits",
        startDate: <Date> new Date(new Date().setDate(new Date().getDate() - 900)),
        startDateStr: <string> "",
        data: {labels: [], datasets: <unknown> [{}], }
    }),
    async mounted () {
        this.loaded = false
        this.startDateStr = this.startDate.toISOString().split('T')[0]
        this.getData()
        this.loaded = true

    },
    watch: {
        "$i18n.locale": async function(){
            this.getData()
            this.$refs.line.chart.update()
        },
    },
    methods: {
        changedWiki: function(event: string){
            this.wiki = event
            this.getData()
            this.$refs.line.chart.update()
        },
        changedDataType: function(event: DataType){
            this.dataType = event
            this.getData()
            this.$refs.line.chart.update()
        },
        changedStartDate: function(event: string){
            this.startDateStr = event
            console.log(`changed start date to ${event}`)
            this.getData()
            this.$refs.line.chart.update()
        },
        getData: async function(){
            try {
                const snapshotUrl = new URL(`${host}/snapshots`)
                snapshotUrl.searchParams.append('limit', '1000')
                snapshotUrl.searchParams.append('wiki', this.wiki)
                snapshotUrl.searchParams.append('after', this.startDateStr)
                snapshotUrl.searchParams.append('type', 'periodical')
                const snapshots  = await fetch(snapshotUrl)
                const apiData = await snapshots.json()
                
                this.data = {
                    labels: apiData.map(function(item:any){
                        return item["timestamp"].slice(0,10)
                    }),
                    datasets: chartConfig.dataSets(apiData, this.dataType, this)
                }
        } catch (e) {
        console.error(e)
        }

        }
    }

}
</script>
<style scoped>
    Line {
        display: inline;
        margin: 0 2rem 0 0;
        
    }
</style>

