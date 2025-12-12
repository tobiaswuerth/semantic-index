import { reactive, readonly, toRef, computed } from 'vue'
import { getCreateDateHistogram, getModifyDateHistogram } from '@/composables/useAPI'

export interface DateRange {
  startDate: Date
  startPercent: number
  endDate: Date
  endPercent: number
}

const state = reactive({
  createDateHistData: null as [Date, number][] | null,
  filterCreateDateRange: null as DateRange | null,

  modifyDateHistData: null as [Date, number][] | null,
  filterModifyDateRange: null as DateRange | null,

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

  return {
    getCreateDateHistData,
    filterCreateDateRange: toRef(state, 'filterCreateDateRange'),

    getModifyDateHistData,
    filterModifyDateRange: toRef(state, 'filterModifyDateRange'),

    totalFiltersActive,
    showDrawer: toRef(state, 'showDrawer'),
    state: readonly(state),
  }
}
