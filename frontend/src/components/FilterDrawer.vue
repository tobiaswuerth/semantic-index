<script setup lang="ts">
import { ref, onMounted } from 'vue'
import type { Ref } from 'vue'
import type { DateRange } from '@/composables/useFilter';
import type { SourceTypeCount } from '@/dto/sourceTypeCount';
import HistDateRangeSelector from './HistDateRangeSelector.vue'
import { useFilter } from '@/composables/useFilter';
import SourceTypeBadge from './SourceTypeBadge.vue';

const {
    getCreateDateHistData,
    filterCreateDateRange,
    getModifyDateHistData,
    filterModifyDateRange,
    getSourceTypesData,
    filterSourceTypes,
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

const sourceTypeData = ref<SourceTypeCount[] | null>(null);
const sourceTypeLoading = ref<boolean>(true);

const loadSourceTypes = async () => {
    sourceTypeData.value = await getSourceTypesData();
    sourceTypeLoading.value = false;
};
const reset = () => {
    filterSourceTypes.value = sourceTypeData.value?.map(stype => stype.source_type.id) || [];
};

onMounted(() => {
    loadSourceTypes();
});

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

            <Divider />

            <div>
                <div class="source-type-filter-header">
                    <h4>Source Types</h4>
                    <Button variant="text" icon="pi pi-refresh" size="small" @click="reset"
                        v-tooltip="'Reset Filter'" />
                </div>
                <div v-if="sourceTypeLoading">
                    <span class="pi pi-spin pi-spinner"></span> Loading histogram...
                </div>
                <div v-else>
                    <div v-for="stype in sourceTypeData" :key="stype.source_type.id" class="p-field-checkbox">
                        <Checkbox :inputId="`stype-${stype.source_type.id}`" :value="stype.source_type.id"
                            v-model="filterSourceTypes" />
                        <label :for="`stype-${stype.source_type.id}`">
                            <SourceTypeBadge :sourceType="stype.source_type" />
                            <small>({{ stype.count }} Sources )</small>
                        </label>

                    </div>
                </div>
            </div>

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
.source-type-filter-header {
    display: flex;
    align-items: center;
}

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