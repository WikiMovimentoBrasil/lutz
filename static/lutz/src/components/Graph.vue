<template>
  <Line v-if="loaded" :data="data" ref="line"/>
  <div v-else> {{$t("message.loading")}}</div>
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
    name: 'App',
    components: {
        Line
    },
    data: () => ({
        loaded: false,
        data: {labels: [], datasets: [{}], }
    }),
    async mounted () {
        this.loaded = false

        try {
        const snapshots  = await fetch(`${host}/snapshots?limit=1000&wiki=ptwiki`)
        const apiData = await snapshots.json()
        
        const dataType = "%_of_editors"
        this.data = {
            labels: apiData.map(function(item:any){
                return item["timestamp"].slice(0,10)
            }),
            datasets: chartConfig.dataSets(apiData, dataType, this)
        }
        this.loaded = true
        } catch (e) {
        console.error(e)
        }
    },
    watch: {
        "$i18n.locale": async function(){
            //TODO refactor to reuse existing data and only change labels
            const snapshots  = await fetch(`${host}/snapshots?limit=1000&wiki=ptwiki`)
            const apiData = await snapshots.json()
            
            const dataType = "%_of_editors"
            this.data = {
                labels: apiData.map(function(item:any){
                    return item["timestamp"].slice(0,10)
                }),
                datasets: chartConfig.dataSets(apiData, dataType, this)
            }
            this.$refs.line.chart.update()
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

