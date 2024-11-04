<template>
  <div class="toolbar">
    <div>
      <span>货币:</span>
      <input type="radio" id="usd" value="USD" v-model="currency" />
      <label for="usd">美元</label>

      <input type="radio" id="cny" value="CNY" v-model="currency" />
      <label for="cny">人民币</label>

      <span style="padding: 0px 0px 0px 10px ;">单价单位:</span>
      <input type="radio" id="unitK" value="K" v-model="unit" />
      <label for="unitK">K</label>

      <input type="radio" id="unitM" value="M" v-model="unit" />
      <label for="unitM">M</label>
    </div>
    <div class="line">
      <label for="input" style="padding: 0px 5px 0px 5px; width: 4rem;">Input</label>
      <input type="text" id="input" style="width: 5rem;" v-model="userInput" />
    </div>
    <div class="line" >
      <label for="output" style="padding: 0px 5px 0px 5px; width: 4rem;">Output</label>
      <input type="text" id="output" style="width: 5rem;"  v-model="userOutput" />
    </div>
    <div class="line">
      <label for="usdToCny" style="padding: 0px 5px 0px 5px; width: 4rem;">USD/CNY</label>
      <input type="number" id="usdToCny" style="width: 5rem;"  v-model="usdToCny" />
    </div>

  </div>

  <div ref="llmTableNode"></div>

</template>

<script setup lang="ts">
import {CellComponent, ColumnDefinition, TabulatorFull as Tabulator} from 'tabulator-tables';
import rawDataUrl from './assets/llm.json?url';
import { onMounted, ref, watch } from 'vue';


type LlmItem = {
  provider: string;
  model: string;
  input: number;
  output: number;
  url: string;
  price?: number;
}

type RawItem = {
  unit: 'K' | 'M'
  currency: 'USD' | 'CNY'
} & LlmItem;


const unit = ref<'K'|'M'>('K');
const currency = ref<'USD'|'CNY'>('CNY');
const userInput = ref('2K');
const userOutput = ref('0.5K');
const usdToCny = ref(7.13);
const table = ref<Tabulator>();
const llmTableNode = ref()
const rawData = ref<RawItem[]>([]);

function price(num: number, item: RawItem) : number {
  if (item.currency !== currency.value) {
    if (item.currency === 'USD') {
      num = num * usdToCny.value;
    } else {
      num = num / usdToCny.value;
    }
  }
  if (item.unit !== unit.value) {
    if (item.unit === 'K') {
      num = num * 1000;
    } else {
      num = num / 1000;
    }
  }
  return num;
} 

function parseUser(text: string) : number {
  if (!text) {
    return 0;
  }
  text = text.replace(/,/g, '');
  if (text.endsWith('K')) {
    return parseFloat(text) * 1000;
  } else if (text.endsWith('M')) {
    return parseFloat(text) * 1000000;
  } else {
    return parseFloat(text);
  }
}

function buildData() : LlmItem[] {
  return rawData.value.map((item: RawItem) => {
    const input = price(item.input, item);
    const output = price(item.output, item);
    const uintValue = unit.value === 'K' ? 1000 : 1000000;
    const userPrice = (input * parseUser(userInput.value)  +output *  parseUser(userOutput.value))/uintValue;
    return {
      provider: item.provider,
      model: item.model,
      input,
      output,
      url: item.url,
      price: Number.parseFloat(userPrice.toFixed(5)),
    }
  }) as LlmItem[]
}

function highlightModel(cell: CellComponent ): string {
  const value = cell.getValue();
  if (value.includes('gpt')) {
    return `<span style="color:blue; font-weight:bold;">${value}</span>`;
  } else if (value.includes('gemini')){
    return `<span style="color:green; font-weight:bold;">${value}</span>`;
  } else if (['haiku', 'sonnet', 'opus'].includes(value)){
    return `<span style="color:purple; font-weight:bold;">${value}</span>`;
  }
  else{
    return value;
  }
}

function buildColumns() : ColumnDefinition[] {
  const precision = currency.value === 'USD' ? 5 : 5;
  //const unitSymbol = unit.value === 'K' ? '/K' : '/M';
  const symbol = (currency.value === 'USD' ? '$' : '¥')

  const formatterParams = {precision, symbol, thousand: ','};

  return [
    {title: 'Provider', field: 'provider', width: 100},
    {title: 'Model', field: 'model', width: 200, formatter: highlightModel},
    {title: 'Price', field: 'price', width: 80, formatter: 'money', formatterParams, hozAlign: 'right'},
    {title: 'Input', field: 'input', width: 100, formatter: 'money', formatterParams, hozAlign: 'right'},
    {title: 'Output', field: 'output', width: 100, formatter: 'money', formatterParams, hozAlign: 'right'},
    {title: 'URL', field: 'url', minWidth: 300, formatter: 'link'}
  ]
}

watch([unit, currency, userInput, userOutput, usdToCny], () => {
  console.log('update', unit.value, currency.value, userInput.value, userOutput.value, usdToCny.value);
  table.value?.setColumns(buildColumns());
  table.value?.replaceData(buildData());
});


onMounted(async () => {
  rawData.value = await ( await fetch(rawDataUrl)).json();
  table.value = new Tabulator(llmTableNode.value, {
    reactiveData: true,
    data: buildData(),
    layout: 'fitColumns',
    columns: buildColumns(),
  });
});

</script>

<style scoped>
.toolbar {
  display: flex;
  justify-content: space-between;
  margin: 10px;
  gap: 10px;
  justify-items: center;
}

@media (max-width: 600px) {
  .toolbar {
    flex-direction: column;
    margin: 10px;
    gap: 10px;
    justify-items: center;
  }
}

.line {
  display: flex;
  justify-items: center;
}
</style>
