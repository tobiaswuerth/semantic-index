<script setup lang="ts">
import { ref, onMounted, useTemplateRef, computed } from 'vue'
import type { DateRange } from '@/composables/useFilter';
import * as echarts from 'echarts';


interface Props {
    title: string
    rangeSelection: DateRange
    fetchHistogramFn: () => Promise<[Date, number][]>
}
const props = defineProps<Props>()

const formatDate = (date: Date): string => {
    return date.toISOString().split('T')[0];
}

const isLoadingData = ref(true);
const histData = ref<[Date, number][]>([]);
const chartContainer = useTemplateRef('chart-div');
let chart: echarts.EChartsType | null = null;

const initChart = async () => {
    isLoadingData.value = true;
    const data_promise = props.fetchHistogramFn()

    const isDark = document.documentElement.classList.contains('dark');
    chart = echarts.init(chartContainer.value, isDark ? 'dark' : 'light');

    const updateRangeSelection = (start: number, end: number) => {
        const startIndex = Math.floor((start / 100) * (histData.value.length - 1));
        const endIndex = Math.ceil((end / 100) * (histData.value.length - 1));

        const startDate = new Date(histData.value[startIndex][0]);

        // at this point end date is something like 2025-12-01, where 01 is always the first day of month
        // however, for endDate we want the last day of the month, so we need to adjust it + 1 month, -1 day
        var endDate = new Date(histData.value[endIndex][0]);
        endDate.setMonth(endDate.getMonth() + 1);
        endDate.setDate(endDate.getDate() - 1);

        props.rangeSelection.startDate = startDate;
        props.rangeSelection.startPercent = start;
        props.rangeSelection.endDate = endDate;
        props.rangeSelection.endPercent = end;
    };

    chart.on('dataZoom', function (params: any) {
        if (params.batch) {
            params = params.batch[0];
        }
        updateRangeSelection(params.start, params.end);
    });

    histData.value = await data_promise;
    updateRangeSelection(props.rangeSelection.startPercent, props.rangeSelection.endPercent);

    const option = {
        xAxis: {
            type: 'time',
            show: false
        },
        yAxis: {
            type: 'value',
            show: false
        },
        dataZoom: [
            {
                type: 'inside',
                start: props.rangeSelection.startPercent,
                end: props.rangeSelection.endPercent,
            },
            {
                type: 'slider',
                left: -3,
                right: 3,
                bottom: -3,
                top: -16,
                borderColor: 'transparent',
                textStyle: null,
            }
        ],
        series: [
            {
                type: 'line',
                data: histData.value,
                showSymbol: false,
                lineStyle: { opacity: 0 },
                areaStyle: { opacity: 0 },
            }
        ],
    };
    chart.setOption(option);
    isLoadingData.value = false
}
const reset = () => {
    if (!chart) {
        return;
    }

    chart.dispatchAction({
        type: 'dataZoom',
        start: 0,
        end: 100
    });
}

const entriesInDataRange = computed(() => {
    const startDate = props.rangeSelection.startDate;
    const endDate = props.rangeSelection.endDate;

    let total = 0;
    for (const [date, count] of histData.value) {
        if (date >= startDate && date <= endDate) {
            total += count;
        }
    }
    return total;
})

onMounted(() => {
    initChart()
})
</script>

<template>
    <div>
        <div class="date-range-header">
            <h4> {{ props.title }}</h4>
            <Button variant="text" icon="pi pi-refresh" size="small" @click="reset" />
            <small>({{ entriesInDataRange }} Sources)</small>
        </div>
        <div v-if="isLoadingData">
            <span class="pi pi-spin pi-spinner"></span> Loading histogram...
        </div>
        <div v-bind:class="{ 'hidden': isLoadingData }" class="chart-container">
            <div class="chart" ref="chart-div"> </div>
            <div class="date-preview">
                <span>{{ formatDate(rangeSelection.startDate) }}</span>
                <span>{{ formatDate(rangeSelection.endDate) }}</span>
            </div>
        </div>
    </div>

</template>

<style scoped>
.date-range-header {
    display: flex;
    align-items: center;
}

.chart-container {
    width: 100%;
    margin-bottom: 1rem;
}

.chart-container .chart {
    width: 100%;
    height: 50px;
    border: 1px solid rgba(119, 119, 119, 0.3);
    border-radius: 5px;
}

.date-preview {
    display: flex;
    justify-content: space-between;
    font-size: 0.875rem;
    margin-top: 0.25rem;
}

.hidden {
    opacity: 0;
}
</style>