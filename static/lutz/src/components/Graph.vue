<template>
  <GraphOptions> </GraphOptions>
  <Line v-if="loaded" :data="data" ref="line" />
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
        data: {labels: [], datasets: [{}], }
    }),
    async mounted () {
        this.loaded = false
        this.getData()
        this.loaded = true

    },
    watch: {
        "$i18n.locale": async function(){
            this.getData()
            this.$refs.line.chart.update()
        },
        "GraphOptions.select": async function(event){
            this.wiki = event
            this.getData()
            this.$refs.line.chart.update()
        }
    },
    methods: {
        getData: async function(){
            try {
                const snapshots  = await fetch(`${host}/snapshots?limit=1000&wiki=${this.wiki}`)
                const apiData = await snapshots.json()
                
                const dataType = "%_of_editors"
                this.data = {
                    labels: apiData.map(function(item:any){
                        return item["timestamp"].slice(0,10)
                    }),
                    datasets: chartConfig.dataSets(apiData, dataType, this)
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

