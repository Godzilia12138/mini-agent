<template>
  <label class="thinking-toggle" :class="{ on: modelValue, disabled }">
    <input
      type="checkbox"
      :checked="modelValue"
      :disabled="disabled"
      @change="onChange"
    />
    <span class="toggle-track"><span class="toggle-thumb" /></span>
    <span class="toggle-label">🧠 深度思考</span>
  </label>
</template>

<script>
export default {
  props: {
    modelValue: { type: Boolean, default: false },
    disabled: { type: Boolean, default: false },
  },
  emits: ["update:modelValue", "change"],
  methods: {
    onChange(e) {
      const val = e.target.checked;
      this.$emit("update:modelValue", val);
      this.$emit("change", val);
    },
  },
};
</script>

<style scoped>
.thinking-toggle {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  user-select: none;
  padding: 4px 10px 4px 6px;
  border-radius: 8px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  background: rgba(255, 255, 255, 0.03);
  transition: all 0.2s;
}

.thinking-toggle.on {
  border-color: rgba(168, 85, 247, 0.35);
  background: rgba(168, 85, 247, 0.12);
}

.thinking-toggle.disabled { opacity: 0.5; cursor: not-allowed; }

.thinking-toggle input { display: none; }

.toggle-track {
  width: 32px;
  height: 18px;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.15);
  position: relative;
  transition: background 0.2s;
}

.thinking-toggle.on .toggle-track {
  background: rgba(168, 85, 247, 0.55);
}

.toggle-thumb {
  position: absolute;
  top: 2px;
  left: 2px;
  width: 14px;
  height: 14px;
  border-radius: 50%;
  background: #fff;
  transition: transform 0.2s;
}

.thinking-toggle.on .toggle-thumb {
  transform: translateX(14px);
}

.toggle-label {
  font-size: 12px;
  font-weight: 500;
  color: #a1a1aa;
}

.thinking-toggle.on .toggle-label {
  color: #d8b4fe;
}
</style>
