import { ref, computed } from 'vue'
import type { LogFile } from '@/types'

export function useLogTable(filteredLogs: LogFile[]) {
  const selectedLogs = defineModel('selectedLogs', { type: Array, default: () => [] })
  const dtFirst = ref(0)
  const dtRows = ref(10)
  const parsingLogs = ref<string[]>([])

  const selectAllState = computed(() => {
    if (filteredLogs.length === 0) return false
    return filteredLogs.every((log) =>
      (selectedLogs.value as LogFile[]).some((s) => s.id === log.id)
    )
  })

  const setParsing = (logId: string, isParsing: boolean) => {
    if (isParsing) parsingLogs.value.push(logId)
    else parsingLogs.value = parsingLogs.value.filter((id) => id !== logId)
  }

  const onSelectAllChange = (event: { checked?: boolean }) => {
    const checked = event.checked
    const pageIds = new Set(filteredLogs.map((l) => l.id))
    if (checked) {
      const others = (selectedLogs.value as LogFile[]).filter((l) => !pageIds.has(l.id))
      selectedLogs.value = [...others, ...filteredLogs]
    } else {
      selectedLogs.value = (selectedLogs.value as LogFile[]).filter((l) => !pageIds.has(l.id))
    }
  }

  const clearSelection = () => { selectedLogs.value = [] }

  return {
    selectedLogs, dtFirst, dtRows, parsingLogs,
    selectAllState, setParsing, onSelectAllChange, clearSelection,
  }
}
