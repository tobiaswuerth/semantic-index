<script setup lang="ts">
import { usePopup } from '@/composables/usePopup'

const {
  closePopup,
  isShown,
  isError,
  isClosable,
  title,
  icon,
  message
} = usePopup()

</script>

<template>
  <Dialog :visible="isShown" modal :closable="isClosable" :dismissableMask="isClosable">
    <template #container>
      <div :class="`popup-container ${isError ? 'popup-error' : ''}`">
        <div class="popup-header">
          <div v-if="!!icon" class="popup-icon">
            <i :class="icon"></i>
          </div>
          <h4 style="flex-grow: 1;">{{ $t(title) }}</h4>
          <Button v-if="isClosable" icon="pi pi-times" text class="p-button-sm" @click="closePopup"
            severity="contrast" />
        </div>
        <template v-if="!!message">
          <div class="popup-message">
            {{ $t(message) }}
          </div>
        </template>
      </div>
    </template>
  </Dialog>
</template>

<style>
.popup-container {
  padding: 0.8rem 1.5rem;
  width: 90vw;
  max-width: 400px;
}

.popup-error {
  background-color: #9e2c2c;
  border-radius: .7rem;
  color: white;
}

.popup-header {
  display: flex;
  align-items: center;
}

.popup-message {
  margin-top: .5rem;
}

.popup-icon {
  margin-right: 1rem;
  padding-top: .2rem
}
</style>
