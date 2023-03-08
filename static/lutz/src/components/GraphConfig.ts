
export function dataSets(apiData:any, type:DataType, component:any) {
    const datasets =  [
        {
        label: component.$t("message.Female"),
        data: 
            apiData.map(function(item:any){
                return item["results"][type]["female"]
            }),
        tension: 0.1
    },
    {
        label: component.$t("message.Male"),
        data: 
            apiData.map(function(item:any){
                return item["results"][type]["male"]
            }),
        tension: 0.1
    },
    {
        label: component.$t("message.Neutral"),
        data: 
            apiData.map(function(item:any){
                return item["results"][type]["neutral"]
            }),
        tension: 0.1
    },
]
    return datasets

}

export type DataType = "%_of_editors"|  "%_of_edits" | "count"| "editcount"
