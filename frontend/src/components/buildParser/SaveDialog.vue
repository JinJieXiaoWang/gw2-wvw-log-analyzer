<template>
  <Dialog
    :visible="visible"
    header="保存Build配置"
    :modal="true"
    :style="{ width: '500px' }"
    @update:visible="emit('update:visible', $event)"
  >
    <form @submit.prevent="handleSubmit" class="space-y-4">
      <!-- Build名称 -->
      <div>
        <label class="block text-sm font-medium text-neutral-text mb-2">
          Build名称 <span class="text-red-500">*</span>
        </label>
        <InputText
          v-model="formData.title"
          class="w-full"
          placeholder="输入Build名称"
          :class="{ 'p-invalid': errors.title }"
        />
        <p v-if="errors.title" class="mt-1 text-sm text-red-500">
          {{ errors.title }}
        </p>
      </div>

      <!-- 职业 -->
      <div>
        <label class="block text-sm font-medium text-neutral-text mb-2">
          职业 <span class="text-red-500">*</span>
        </label>
        <Dropdown
          v-model="formData.profession"
          :options="professionOptions"
          option-label="label"
          option-value="value"
          class="w-full"
          placeholder="选择职业"
          :class="{ 'p-invalid': errors.profession }"
        />
        <p v-if="errors.profession" class="mt-1 text-sm text-red-500">
          {{ errors.profession }}
        </p>
      </div>

      <!-- 职责 -->
      <div>
        <label class="block text-sm font-medium text-neutral-text mb-2">
          职责 <span class="text-red-500">*</span>
        </label>
        <Dropdown
          v-model="formData.role"
          :options="roleOptions"
          option-label="label"
          option-value="value"
          class="w-full"
          placeholder="选择职责"
          :class="{ 'p-invalid': errors.role }"
        />
        <p v-if="errors.role" class="mt-1 text-sm text-red-500">
          {{ errors.role }}
        </p>
      </div>

      <!-- 备注 -->
      <div>
        <label class="block text-sm font-medium text-neutral-text mb-2">
          备注
        </label>
        <Textarea
          v-model="formData.notes"
          class="w-full"
          placeholder="添加备注说明（可选）"
          rows="3"
        />
      </div>

      <!-- 是否为Meta Build -->
      <div class="flex items-center gap-2">
        <Checkbox
          v-model="formData.isMeta"
          input-id="isMeta"
        />
        <label for="isMeta" class="text-sm text-neutral-text">
          标记为Meta Build
        </label>
      </div>
    </form>

    <template #footer>
      <Button
        label="取消"
        class="btn-ghost"
        @click="handleClose"
      />
      <Button
        label="保存"
        class="btn-game"
        :loading="isSaving"
        @click="handleSubmit"
      />
    </template>
  </Dialog>
</template>

<script setup lang="ts">
/**
 * 保存Build对话框组件
 * 功能：保存Build配置到服务器
 * 作者：帅姐姐
 * 创建日期：2026-05-04
 */

import { ref, watch } from 'vue';
import Dialog from 'primevue/dialog';
import InputText from 'primevue/inputtext';
import Dropdown from 'primevue/dropdown';
import Textarea from 'primevue/textarea';
import Button from 'primevue/button';
import Checkbox from 'primevue/checkbox';


// Props
const props = defineProps<{
  visible: boolean;
  parsedData?: any;
  buildCode?: string;
}>();

// Emits
const emit = defineEmits<{
  'update:visible': [value: boolean];
  'save': [data: any];
}>();

// 状态
const isSaving = ref(false);
const formData = ref({
  title: '',
  profession: '',
  eliteSpec: null as string | null,
  role: '',
  subRoles: [] as string[],
  armorType: '',
  weapons: [] as any[],
  relic: '',
  rune: '',
  food: '',
  wrench: '',
  infusion: '',
  attrRequirements: [] as string[],
  bdCode: '',
  traitLines: [] as any[],
  rotationCommands: [] as any[],
  mechanics: [] as any[],
  videos: [] as any[],
  author: '',
  notes: '',
  isMeta: false
});

const errors = ref<{
  title?: string;
  profession?: string;
  role?: string;
}>({});

// 职业选项
const professionOptions = [
  { label: '战士', value: 'Warrior' },
  { label: '守护者', value: 'Guardian' },
  { label: '魂武者', value: 'Revenant' },
  { label: '游侠', value: 'Ranger' },
  { label: '工程师', value: 'Engineer' },
  { label: '唤灵师', value: 'Necromancer' },
  { label: '幻术师', value: 'Mesmer' },
  { label: '元素使', value: 'Elementalist' }
];

// 职责选项
const roleOptions = [
  { label: 'DPS', value: 'dps' },
  { label: '辅助', value: 'support' }
];

// 监听visible变化，初始化表单
watch(() => props.visible, (newVal) => {
  if (newVal) {
    initializeForm();
  }
});

// 初始化表单
const initializeForm = () => {
  if (props.parsedData) {
    formData.value = {
      title: '',
      profession: props.parsedData.profession || '',
      eliteSpec: props.parsedData.elite_spec || null,
      role: '',
      subRoles: [],
      armorType: props.parsedData.armor_type || '',
      weapons: props.parsedData.weapons || [],
      relic: props.parsedData.relic || '',
      rune: props.parsedData.rune || '',
      food: '',
      wrench: '',
      infusion: '',
      attrRequirements: [],
      bdCode: props.buildCode || '',
      traitLines: props.parsedData.traits || [],
      rotationCommands: [],
      mechanics: [],
      videos: [],
      author: '',
      notes: '',
      isMeta: false
    };
  }
  errors.value = {};
};

// 验证表单
const validateForm = (): boolean => {
  errors.value = {};
  let isValid = true;

  if (!formData.value.title.trim()) {
    errors.value.title = '请输入Build名称';
    isValid = false;
  }

  if (!formData.value.profession) {
    errors.value.profession = '请选择职业';
    isValid = false;
  }

  if (!formData.value.role) {
    errors.value.role = '请选择职责';
    isValid = false;
  }

  return isValid;
};

// 提交表单
const handleSubmit = async () => {
  if (!validateForm()) {
    return;
  }

  isSaving.value = true;

  try {
    emit('save', formData.value);
  } catch (error) {
    console.error('保存失败:', error);
  } finally {
    isSaving.value = false;
  }
};

// 关闭对话框
const handleClose = () => {
  emit('update:visible', false);
};
</script>