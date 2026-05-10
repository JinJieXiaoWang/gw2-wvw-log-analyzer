import { ref, computed, watch, onMounted, onBeforeUnmount } from 'vue'

export const PRESET_COLORS = [
  { value: '#165DFF', label: '电竞蓝' }, { value: '#4080FF', label: '浅蓝' },
  { value: '#FF7D00', label: '战火橙' }, { value: '#FBCF4B', label: '金黄' },
  { value: '#00C896', label: '科技青' }, { value: '#00B42A', label: '成功绿' },
  { value: '#F53F3F', label: '危险红' }, { value: '#722ED1', label: '神秘紫' },
  { value: '#E5E5E5', label: '常规文字' }, { value: '#909399', label: '次要文字' },
  { value: '#141414', label: '深色背景' }, { value: '#2A2A2A', label: '卡片背景' },
  { value: '#333333', label: '分割线' }, { value: '#FFFFFF', label: '纯白' },
  { value: '#000000', label: '纯黑' }, { value: '#1f77b4', label: '标准蓝' }
]

export const CLASS_NAME_OPTIONS = ['primary', 'secondary', 'success', 'danger', 'warning', 'info', 'contrast']

export function useColorPicker(props: { modelValue: string }, emit: { (e: 'update:modelValue', value: string): void }) {
  const isOpen = ref(false)
  const pickerRef = ref<HTMLElement>()
  const customHexInput = ref('')
  const customError = ref('')

  const isValidHex = computed(() => /^#([0-9A-Fa-f]{6}|[0-9A-Fa-f]{3})$/.test(props.modelValue))
  const isClassName = computed(() => props.modelValue && !props.modelValue.startsWith('#'))
  const isValidCustomHex = computed(() => /^[0-9A-Fa-f]{6}$/.test(customHexInput.value))

  const previewStyle = computed(() => {
    if (isValidHex.value) return { backgroundColor: props.modelValue, borderColor: props.modelValue }
    if (isClassName.value) return { backgroundColor: 'var(--color-primary-alpha-10)', borderColor: 'var(--color-primary)' }
    return {}
  })

  function togglePanel() {
    isOpen.value = !isOpen.value
    if (isOpen.value) {
      const hex = props.modelValue?.replace('#', '') || ''
      customHexInput.value = /^[0-9A-Fa-f]{6}$/.test(hex) ? hex.toUpperCase() : ''
      customError.value = ''
    }
  }

  function closePanel() { isOpen.value = false }

  function selectColor(color: string) { emit('update:modelValue', color); customError.value = '' }
  function clearColor() { emit('update:modelValue', ''); customHexInput.value = ''; customError.value = '' }
  function handleInputChange(value: string | undefined) { emit('update:modelValue', value || '') }

  function applyCustomHex() {
    const input = customHexInput.value.trim().toUpperCase()
    if (!input) { customError.value = ''; return }
    if (!/^[0-9A-Fa-f]{6}$/.test(input)) { customError.value = '请输入有效的 6 位十六进制颜色码（如 FF7D00）'; return }
    emit('update:modelValue', '#' + input)
    customError.value = ''
  }

  watch(() => props.modelValue, (newVal) => {
    if (!isOpen.value) return
    const hex = newVal?.replace('#', '') || ''
    if (/^[0-9A-Fa-f]{6}$/.test(hex)) { customHexInput.value = hex.toUpperCase(); customError.value = '' }
  })

  function handleClickOutside(event: MouseEvent) {
    if (pickerRef.value && !pickerRef.value.contains(event.target as Node)) isOpen.value = false
  }

  onMounted(() => document.addEventListener('click', handleClickOutside))
  onBeforeUnmount(() => document.removeEventListener('click', handleClickOutside))

  return {
    isOpen, pickerRef, customHexInput, customError,
    isValidHex, isClassName, isValidCustomHex, previewStyle,
    togglePanel, closePanel, selectColor, clearColor, handleInputChange, applyCustomHex
  }
}
