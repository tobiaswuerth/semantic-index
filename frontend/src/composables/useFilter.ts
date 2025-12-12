import { reactive, readonly, toRef, computed } from 'vue'
import { getCreateDateHistogram, getModifyDateHistogram, getSourceTypeCounts } from '@/composables/useAPI'
import type { SourceTypeCount } from '@/dto/sourceTypeCount'
import type { HistogramResponse } from '@/dto/histogramResponse'

export interface DateRange {
  startDate: Date
  startPercent: number
  endDate: Date
  endPercent: number
}

const state = reactive({
  createDateHistData: null as HistogramResponse[] | null,
  filterCreateDateRange: null as DateRange | null,

  modifyDateHistData: null as HistogramResponse[] | null,
  filterModifyDateRange: null as DateRange | null,

  sourceTypesData: null as SourceTypeCount[] | null,
  filterSourceTypes: null as number[] | null,

  showDrawer: false,
})

const totalFiltersActive = computed(() => {
  let count = 0
  if (state.filterCreateDateRange && (state.filterCreateDateRange.startPercent > 0 || state.filterCreateDateRange.endPercent < 100)) {
    count += 1
  }
  if (state.filterModifyDateRange && (state.filterModifyDateRange.startPercent > 0 || state.filterModifyDateRange.endPercent < 100)) {
    count += 1
  }
  if (state.sourceTypesData) {
    count += state.sourceTypesData.length - (state.filterSourceTypes?.length ?? 0)
  }
  return count
})

export function useFilter() {

  const getCreateDateHistData = async () => {
    if (state.createDateHistData !== null) {
      return state.createDateHistData
    }
    state.createDateHistData = await getCreateDateHistogram();
    return state.createDateHistData;
  }
  const getModifyDateHistData = async () => {
    if (state.modifyDateHistData !== null) {
      return state.modifyDateHistData
    }
    state.modifyDateHistData = await getModifyDateHistogram();
    return state.modifyDateHistData;
  }
  const getSourceTypesData = async () => {
    if (state.sourceTypesData !== null) {
      return state.sourceTypesData
    }
    state.sourceTypesData = await getSourceTypeCounts();
    state.filterSourceTypes = state.sourceTypesData.map(st => st.source_type.id);
    return state.sourceTypesData;
  }

  return {
    getCreateDateHistData,
    filterCreateDateRange: toRef(state, 'filterCreateDateRange'),

    getModifyDateHistData,
    filterModifyDateRange: toRef(state, 'filterModifyDateRange'),

    getSourceTypesData,
    filterSourceTypes: toRef(state, 'filterSourceTypes'),

    totalFiltersActive,
    showDrawer: toRef(state, 'showDrawer'),
    state: readonly(state),
  }
}
