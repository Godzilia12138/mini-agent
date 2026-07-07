<template>

  <div class="model-selector">

    <select

      :value="modelValue"

      @change="onChange"

      :disabled="disabled"

      class="model-select"

    >

      <optgroup v-for="group in groupedModels" :key="group.label" :label="group.label">

        <option

          v-for="m in group.items"

          :key="m.id"

          :value="m.id"

          :disabled="!m.available"

        >

          {{ m.is_default ? "★ " : "" }}{{ m.name }}{{ m.available ? "" : " (未配置)" }}

        </option>

      </optgroup>

    </select>

  </div>

</template>



<script>

export default {

  props: {

    models: { type: Array, default: () => [] },

    modelValue: { type: String, default: "" },

    disabled: { type: Boolean, default: false },

  },

  emits: ["update:modelValue", "change"],

  computed: {

    groupedModels() {

      const order = [

        { label: "DeepSeek", match: (m) => m.id.includes("deepseek") || m.name.includes("DeepSeek") },

        { label: "Qwen 通义", match: (m) => m.id.includes("qwen") || m.name.includes("Qwen") },

        { label: "Kimi", match: (m) => m.id === "kimi" || m.id.startsWith("moonshot") || m.id.startsWith("kimi-k") || m.name.includes("Kimi") },

        { label: "GLM 智谱", match: (m) => m.id.includes("glm") || m.name.includes("GLM") },

        { label: "其他", match: () => true },

      ];

      const used = new Set();

      const groups = [];

      for (const g of order) {

        const items = this.models.filter((m) => {

          if (used.has(m.id)) return false;

          if (!g.match(m)) return false;

          used.add(m.id);

          return true;

        });

        if (items.length) groups.push({ label: g.label, items });

      }

      return groups;

    },

  },

  methods: {

    onChange(e) {

      const val = e.target.value;

      this.$emit("update:modelValue", val);

      this.$emit("change", val);

    },

  },

};

</script>



<style scoped>

.model-selector { position: relative; }

.model-select {

  appearance: none;

  background: rgba(99, 102, 241, 0.12);

  border: 1px solid rgba(99, 102, 241, 0.25);

  color: #a5b4fc;

  font-size: 12px;

  font-weight: 500;

  padding: 5px 28px 5px 10px;

  border-radius: 8px;

  cursor: pointer;

  outline: none;

  min-width: 160px;

  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 24 24' fill='none' stroke='%23a5b4fc' stroke-width='2'%3E%3Cpolyline points='6 9 12 15 18 9'/%3E%3C/svg%3E");

  background-repeat: no-repeat;

  background-position: right 8px center;

}

.model-select:hover:not(:disabled) {

  background-color: rgba(99, 102, 241, 0.2);

}

.model-select:disabled { opacity: 0.5; cursor: not-allowed; }

.model-select option, .model-select optgroup {

  background: #111118;

  color: #e4e4e7;

}

</style>


