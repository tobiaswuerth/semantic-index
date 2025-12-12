<script setup lang="ts">
import { ref } from 'vue'
import type { Ref } from 'vue'
import HistDateRangeSelector from './HistDateRangeSelector.vue'
import { useFilter } from '@/composables/useFilter';
import type { DateRange } from '@/composables/useFilter';

const {
    getCreateDateHistData,
    filterCreateDateRange,
    getModifyDateHistData,
    filterModifyDateRange,
    showDrawer,
} = useFilter();

const ensureDateRange = (dateRange: DateRange | null): DateRange => {
    if (dateRange) {
        return {
            startDate: dateRange.startDate,
            startPercent: dateRange.startPercent,
            endDate: dateRange.endDate,
            endPercent: dateRange.endPercent
        };
    } else {
        return {
            startDate: new Date(),
            startPercent: 0,
            endDate: new Date(),
            endPercent: 100
        };
    }
};

const filterCreateDateRangeTmp: Ref<DateRange> = ref(ensureDateRange(filterCreateDateRange.value));
const filterModifyDateRangeTmp: Ref<DateRange> = ref(ensureDateRange(filterModifyDateRange.value));

const applyFilters = () => {
    filterCreateDateRange.value = filterCreateDateRangeTmp.value;
    filterModifyDateRange.value = filterModifyDateRangeTmp.value;
    showDrawer.value = false;
};

const cancel = () => {
    filterCreateDateRangeTmp.value = ensureDateRange(filterCreateDateRange.value);
    filterModifyDateRangeTmp.value = ensureDateRange(filterModifyDateRange.value);
};

</script>

<template>
    <Drawer v-model:visible="showDrawer" position="right" :dismissable="false" :blockScroll="true"
        v-on:after-hide="cancel" :close-on-escape="false">
        <template #header>
            <div class="title">Search Filters</div>
        </template>
        <div>
            <Divider />

            <HistDateRangeSelector :fetchHistogramFn="getCreateDateHistData" :rangeSelection="filterCreateDateRangeTmp"
                title="Created Date" />
            <HistDateRangeSelector :fetchHistogramFn="getModifyDateHistData" :rangeSelection="filterModifyDateRangeTmp"
                title="Modified Date" />

        </div>
        <template #footer>
            <Divider />
            <div class="action-buttons">
                <Button label="Apply Filters" icon="pi pi-check" @click="applyFilters" />
                <Button label="Cancel" icon="pi pi-times" variant="outlined" @click="showDrawer = false" />
            </div>
        </template>
    </Drawer>
</template>

<style scoped>
.title {
    font-weight: 600;
}

.action-buttons {
    display: flex;
    justify-content: center;
    gap: 1rem;
}

.action-buttons:first-child {
    flex-grow: 1;
}
</style>