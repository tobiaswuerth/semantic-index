import { reactive, readonly, toRef, computed } from 'vue'
import { getCreateDateHistogram, getModifyDateHistogram, getTagCounts } from '@/composables/useAPI'
import type { TagCount } from '@/dto/tagCount'
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

  tagData: null as TagCount[] | null,
  filterTags: null as number[] | null,

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
  if (state.tagData) {
    count += state.tagData.length - (state.filterTags?.length ?? 0)
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
  const getTagData = async () => {
    if (state.tagData !== null) {
      return state.tagData
    }
    state.tagData = await getTagCounts();
    state.filterTags = state.tagData.map(st => st.tag.id);
    return state.tagData;
  }

  return {
    getCreateDateHistData,
    filterCreateDateRange: toRef(state, 'filterCreateDateRange'),

    getModifyDateHistData,
    filterModifyDateRange: toRef(state, 'filterModifyDateRange'),

    getTagData,
    filterTags: toRef(state, 'filterTags'),

    totalFiltersActive,
    showDrawer: toRef(state, 'showDrawer'),
    state: readonly(state),
  }
}
