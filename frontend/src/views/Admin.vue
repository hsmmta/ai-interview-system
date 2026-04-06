<template>
  <div class="admin-container">
    <div class="header">
      <h2>后台管理 - 知识图谱</h2>
      <button class="btn-logout" @click="handleLogout">退出登录</button>
    </div>
    <div class="content">
      <div class="toolbar">
        <button class="btn-primary" @click="showAddModal = true">添加节点</button>
        <button class="btn-danger" style="width: auto; margin-left: 10px;" @click="showDeleteModal = true">删除节点</button>
      </div>

      <div class="graph-view">
        <div v-if="errorMsg" class="error-msg">
          <p>{{ errorMsg }}</p>
        </div>
        <div v-else-if="!hasData" class="placeholder">
          <p>暂无连通数据或正在连接 Neo4j...</p>
          <span>(正在加载可视化图谱...)</span>
        </div>

        <div v-show="hasData" class="graph-layout">
          <div class="network-container" ref="networkContainer"></div>

          <div v-if="selectedNode" class="node-details">
            <h3>节点信息</h3>
            <div class="detail-item">
              <span class="detail-label">类型:</span>
              <span class="detail-value">{{ selectedNode.group }}</span>
            </div>
            <div class="detail-item">
              <span class="detail-label">名称:</span>
              <span class="detail-value">{{ selectedNode.realLabel }}</span>
            </div>
            <div v-if="selectedNode.properties" class="properties-list">
              <h4>详细属性</h4>
              <div v-for="(val, key) in selectedNode.properties" :key="key" class="property-item">
                <span class="property-key">{{ key }}:</span>
                <span class="property-val">{{ val }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 添加节点弹窗 -->
    <div v-if="showAddModal" class="modal-overlay">
      <div class="modal">
        <h3>添加/导入节点</h3>
        <div class="modal-tabs">
          <button :class="{active: addMode === 'manual'}" @click="addMode = 'manual'">手动输入</button>
          <button :class="{active: addMode === 'json'}" @click="addMode = 'json'">JSON 导入</button>
        </div>

        <div v-if="addMode === 'manual'" class="mode-content">
          <div class="form-group">
            <label>节点类型</label>
            <select v-model="manualNode.type">
              <option value="Job">职业岗位 (Job)</option>
              <option value="Tech">知识点 (Tech)</option>
              <option value="Question">面试问题 (Question)</option>
            </select>
          </div>
          <div class="form-group">
            <label>节点内容</label> jie
            <textarea v-model="manualNode.name" rows="2" placeholder="输入名称或题目内容"></textarea>
          </div>
          <div class="form-group">
            <label>指向的上级节点名称 (可选)</label>
            <input v-model="manualNode.parentName" type="text" placeholder="例如：加Tech时填关联的Job名" />
            <small class="hint">填写后将自动建立连接 (如: Tech -> Job, Question -> Tech)</small>
          </div>
        </div>

        <div v-else class="mode-content">
          <div class="form-group">
            <label>上传 JSON 文件 (或直接粘贴内容)</label>
            <input type="file" accept=".json" @change="handleFileUpload" style="margin-bottom: 10px;" />
            <textarea v-model="jsonInput" rows="8" placeholder='[
  { "type": "Job", "name": "AI算法工程师" },
  { "type": "Tech", "name": "深度学习", "parentName": "AI算法工程师" },
  { "type": "Question", "name": "什么是过拟合？", "parentName": "深度学习" }
]'></textarea>
          </div>
        </div>

        <div class="modal-actions">
          <button class="btn-cancel" @click="showAddModal = false">取消</button>
          <button class="btn-confirm" @click="addNode">确认添加</button>
        </div>
      </div>
    </div>

    <!-- 删除节点弹窗 -->
    <div v-if="showDeleteModal" class="modal-overlay">
      <div class="modal">
        <h3>删除知识图谱节点</h3>
        <p class="hint" style="color: #ff4d4f; margin-bottom: 20px; font-weight: bold;">
          注意：删除上级节点将联动删除其下属所有的子节点及连线！
        </p>
        <div class="form-group">
          <label>节点类型</label>
          <select v-model="deleteNodeData.type">
            <option value="Job">职业岗位 (Job) - 将连带删除所属 Tech 和 Question</option>
            <option value="Tech">知识点 (Tech) - 将连带删除所属 Question</option>
            <option value="Question">面试问题 (Question) - 仅删除该问题</option>
          </select>
        </div>
        <div class="form-group">
          <label>要删除的节点名称 / 题干</label>
          <input v-model="deleteNodeData.name" type="text" placeholder="输入准确的节点名称" />
        </div>
        <div class="modal-actions">
          <button class="btn-cancel" @click="showDeleteModal = false">取消</button>
          <button class="btn-danger" style="width: auto;" @click="executeBatchDelete">确认彻底删除</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import neo4j from 'neo4j-driver'
import { Network } from 'vis-network'
import { DataSet } from 'vis-data'

const router = useRouter()
const showAddModal = ref(false)
const showDeleteModal = ref(false)
const addMode = ref('manual')

const manualNode = ref({
  name: '',
  type: 'Tech',
  parentName: ''
})

const deleteNodeData = ref({
  name: '',
  type: 'Job'
})

const jsonInput = ref('')

const graphData = ref([])
const hasData = ref(false)
const errorMsg = ref('')
const networkContainer = ref(null)
const selectedNode = ref(null)
let driver = null
let network = null

// ==========================================
// Neo4j Cloud 配置信息
// ==========================================
const neo4jConfig = {
  uri: import.meta.env.VITE_NEO4J_URI,
  user: import.meta.env.VITE_NEO4J_USER,
  password: import.meta.env.VITE_NEO4J_PASSWORD
}
onMounted(() => {
  initNeo4j()
})

onUnmounted(async () => {
  if (driver) {
    await driver.close()
  }
  if (network) {
    network.destroy()
  }
})
const initNeo4j = async () => {
  try {
    driver = neo4j.driver(
        neo4jConfig.uri,
        neo4j.auth.basic(neo4jConfig.user, neo4jConfig.password)
    )
    await driver.getServerInfo()
    await loadGraphData()
  } catch (err) {
    console.error('Neo4j 连接失败:', err)
    errorMsg.value = '无法连接到 Neo4j，请在代码中检查您的 URI 和凭证配置。'
  }
}

const loadGraphData = async () => {
  if (!driver) return
  const session = driver.session()
  try {
    //  优化 1：改为最稳健的“全局连线提取”查询，直接把所有的节点和关系拉出来，LIMIT 扩大到 800
    const result = await session.run('MATCH (n)-[r]->(m) RETURN n, r, m LIMIT 800')
    const nodesMap = new Map()
    const edgesMap = new Map()

    result.records.forEach(record => {
      const start = record.get('n')
      const end = record.get('m')
      const rel = record.get('r')

      // 判断组别的辅助函数
      const getGroup = (node) => {
        if (node.labels.includes('Job')) return 'Job'
        if (node.labels.includes('Tech')) return 'Tech'
        if (node.labels.includes('Question')) return 'Question'
        return 'default'
      }

      //  优化 2：彻底弃用废弃的 identity.toNumber()，全面使用最新的 elementId (字符串)
      if (!nodesMap.has(start.elementId)) {
        const displayLabel = start.properties.name || start.properties.title || start.labels.join(', ')
        nodesMap.set(start.elementId, {
          id: start.elementId,
          label: displayLabel,
          realLabel: displayLabel,
          title: displayLabel,
          group: getGroup(start),
          properties: start.properties
        })
      }

      if (!nodesMap.has(end.elementId)) {
        const displayLabel = end.properties.name || end.properties.title || end.labels.join(', ')
        nodesMap.set(end.elementId, {
          id: end.elementId,
          label: displayLabel,
          realLabel: displayLabel,
          title: displayLabel,
          group: getGroup(end),
          properties: end.properties
        })
      }

      //  优化 3：连线的起点和终点，使用最新的 startNodeElementId 和 endNodeElementId
      if (!edgesMap.has(rel.elementId)) {
        edgesMap.set(rel.elementId, {
          id: rel.elementId,
          from: rel.startNodeElementId,
          to: rel.endNodeElementId,
          label: rel.type
        })
      }
    })

    const nodesData = Array.from(nodesMap.values())
    const edgesData = Array.from(edgesMap.values())
    hasData.value = nodesData.length > 0

    if (hasData.value) {
      await nextTick()
      const nodes = new DataSet(nodesData)
      const edges = new DataSet(edgesData)
      const data = { nodes, edges }

      const options = {
        nodes: {
          shape: 'dot',
          borderWidth: 1,
          borderWidthSelected: 2,
          //  优化 4：字体放大到 16，并加粗，确保在星空图中清晰可见
          font: { size: 16, color: '#333333', face: 'arial', bold: true }
        },
        groups: {
          Job: {
            size: 28,
            color: { background: '#61e1fa', border: '#b0eeff', highlight: { background: '#61e1fa', border: '#fff' } }
          },
          Tech: {
            size: 20,
            color: { background: '#2cd070', border: '#a5edc1', highlight: { background: '#2cd070', border: '#fff' } }
          },
          Question: {
            size: 14,
            color: { background: '#ffbccb', border: '#ffdce5', highlight: { background: '#ffbccb', border: '#fff' } }
          },
          default: {
            size: 10,
            color: { background: '#a0aec0', border: '#718096' }
          }
        },
        edges: {
          arrows: 'to',
          color: { color: '#cbd5e1', highlight: '#94a3b8' },
          width: 1.5,
          selectionWidth: 3,
          smooth: {
            type: 'continuous'
          },
          length: 150
        },
        layout: {
          improvedLayout: true
        },
        physics: {
          enabled: true,
          solver: 'forceAtlas2Based',
          forceAtlas2Based: {
            gravitationalConstant: -150, // 加大排斥力，让节点散得更开
            centralGravity: 0.015,
            springLength: 200,           // 连线拉长，给文字留出空间
            springConstant: 0.05,
            damping: 0.4,
            avoidOverlap: 0.8            // 极力避免节点和文字重叠
          },
          stabilization: {
            iterations: 200
          }
        },
        interaction: {
          hover: true
        }
      }

      if (network) {
        network.setData(data)
      } else if (networkContainer.value) {
        network = new Network(networkContainer.value, data, options)

        network.on("click", function (params) {
          if (params.nodes.length > 0) {
            const nodeId = params.nodes[0]
            const nodeData = nodesMap.get(nodeId)
            selectedNode.value = nodeData
          } else {
            selectedNode.value = null
          }
        })
      }
    }
  } catch (err) {
    console.error('查询数据失败:', err)
    errorMsg.value = '查询数据失败: ' + err.message
  } finally {
    await session.close()
  }
}

const handleLogout = () => {
  router.push('/login')
}

const handleFileUpload = (event) => {
  const file = event.target.files[0]
  if (!file) return
  const reader = new FileReader()
  reader.onload = (e) => {
    jsonInput.value = e.target.result
  }
  reader.readAsText(file)
}

const addNode = async () => {
  if (!driver) {
    alert('数据库未连接，请先配置 Neo4j 凭证')
    return
  }
  const session = driver.session()
  try {
    if (addMode.value === 'manual') {
      const { name, type, parentName } = manualNode.value
      if (!name.trim()) return alert('请输入节点名称')

      // 使用 MERGE 避免重复创建同名节点
      const label = type.replace(/[^a-zA-Z0-9_]/g, '') // 简单过滤防注入
      await session.run(`MERGE (n:${label} {name: $name}) RETURN n`, { name: name.trim() })

      // 若填写了上级，则自动连线
      if (parentName.trim()) {
        let relType = 'RELATES_TO'
        if (label === 'Tech') relType = 'REQUIRE'
        if (label === 'Question') relType = 'TESTS'

        await session.run(`
          MATCH (child:${label} {name: $childName})
          MATCH (parent {name: $parentName})
          MERGE (child)-[r:${relType}]->(parent)
        `, { childName: name.trim(), parentName: parentName.trim() })
      }
      alert('手动添加成功！')
    } else {
      // JSON 导入模式
      if (!jsonInput.value.trim()) return alert('JSON 内容为空')
      let data = null
      try {
        data = JSON.parse(jsonInput.value)
      } catch (e) {
        return alert('JSON 格式错误，请检查！\n' + e.message)
      }

      if (!Array.isArray(data)) data = [data]

      for (const item of data) {
        const type = (item.type || 'Unknown').replace(/[^a-zA-Z0-9_]/g, '')
        const name = item.name
        if (!name) continue

        await session.run(`MERGE (n:${type} {name: $name})`, { name })

        const pName = item.parentName || item.parentJob || item.parentTech
        if (pName) {
          let relType = 'RELATES_TO'
          if (type === 'Tech') relType = 'REQUIRE'
          if (type === 'Question') relType = 'TESTS'

          await session.run(`
            MATCH (child:${type} {name: $childName})
            MATCH (parent {name: $parentName})
            MERGE (child)-[r:${relType}]->(parent)
          `, { childName: name, parentName: pName })
        }
      }
      alert('JSON 批量导入成功！')
    }

    showAddModal.value = false
    manualNode.value = { name: '', type: 'Tech', parentName: '' }
    jsonInput.value = ''

    await loadGraphData()
  } catch (err) {
    console.error('添加节点/连线失败:', err)
    alert('操作失败: ' + err.message)
  } finally {
    await session.close()
  }
}

const executeBatchDelete = async () => {
  const { name, type } = deleteNodeData.value
  if (!name.trim()) return alert('请输入要删除的节点名称')

  if (!confirm(`确定要彻底删除 [${type}] "${name}" 及其所有子级关系吗？该操作不可恢复！`)) {
    return
  }

  if (!driver) {
    alert('数据库未连接')
    return
  }

  const session = driver.session()
  try {
    let query = ''
    if (type === 'Job') {
      // 删除 Job 以及挂载在它下面的 Tech 和 Question
      query = `
        MATCH (j:Job {name: $name})
        OPTIONAL MATCH (j)<-[:REQUIRE]-(t:Tech)
        OPTIONAL MATCH (t)<-[:TESTS]-(q:Question)
        DETACH DELETE j, t, q
      `
    } else if (type === 'Tech') {
      // 删除 Tech 以及挂载在它下面的 Question
      query = `
        MATCH (t:Tech {name: $name})
        OPTIONAL MATCH (t)<-[:TESTS]-(q:Question)
        DETACH DELETE t, q
      `
    } else if (type === 'Question') {
      // 仅删除单一 Question
      query = `
        MATCH (q:Question {name: $name})
        DETACH DELETE q
      `
    }

    const res = await session.run(query, { name: name.trim() })
    alert(`节点及其子结构已成功删除！`)

    showDeleteModal.value = false
    deleteNodeData.value = { name: '', type: 'Job' }
    selectedNode.value = null // 清空侧边栏选中状态

    await loadGraphData()
  } catch (err) {
    console.error('删除节点失败:', err)
    alert('删除失败: ' + err.message)
  } finally {
    await session.close()
  }
}
</script>

<style scoped>
.admin-container {
  min-height: 100vh;
  background: #f5f7fa;
  padding: 20px;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: white;
  padding: 15px 30px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
  margin-bottom: 20px;
}

.header h2 {
  margin: 0;
  color: #333;
}

.btn-logout {
  background: #ff4d4f;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
}

.content {
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
}

.toolbar {
  margin-bottom: 20px;
}

.btn-primary {
  background: #667eea;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 500;
}

.graph-view {
  height: 600px;
  border: 2px dashed #e2e8f0;
  border-radius: 8px;
  display: flex;
  background: #fafafa;
  flex-direction: column;
}

.graph-layout {
  display: flex;
  width: 100%;
  height: 100%;
}

.network-container {
  flex: 1;
  height: 100%;
}

.node-details {
  width: 300px;
  background: white;
  border-left: 1px solid #e2e8f0;
  padding: 20px;
  overflow-y: auto;
  box-shadow: -2px 0 5px rgba(0,0,0,0.05);
  font-size: 0.95rem;
}

.node-details h3 {
  margin-top: 0;
  color: #333;
  border-bottom: 2px solid #e2e8f0;
  padding-bottom: 10px;
  margin-bottom: 15px;
}

.detail-item {
  margin-bottom: 10px;
}

.detail-label {
  font-weight: bold;
  color: #666;
  margin-right: 8px;
}

.properties-list {
  margin-top: 20px;
}

.properties-list h4 {
  color: #444;
  margin-bottom: 10px;
  font-size: 1rem;
}

.property-item {
  background: #f8fafc;
  padding: 8px 10px;
  border-radius: 4px;
  margin-bottom: 8px;
  word-break: break-all;
}

.property-key {
  font-weight: 500;
  color: #475569;
  margin-right: 5px;
}

.property-val {
  color: #334155;
}

.error-msg {
  color: #ff4d4f;
  margin: auto;
  text-align: center;
}

.placeholder {
  text-align: center;
  color: #94a3b8;
  margin: auto;
}
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0,0,0,0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}
.modal {
  background: white;
  padding: 25px;
  border-radius: 8px;
  width: 500px;
}
.modal-tabs {
  display: flex;
  margin-bottom: 20px;
  border-bottom: 1px solid #e2e8f0;
}
.modal-tabs button {
  flex: 1;
  background: none;
  border: none;
  padding: 10px;
  font-size: 1rem;
  cursor: pointer;
  color: #64748b;
  border-bottom: 2px solid transparent;
}
.modal-tabs button.active {
  color: #667eea;
  border-bottom: 2px solid #667eea;
  font-weight: bold;
}
.mode-content {
  min-height: 250px;
}
.form-group {
  margin-bottom: 15px;
}
.form-group label {
  display: block;
  margin-bottom: 5px;
  color: #334155;
  font-weight: 500;
}
.form-group input, .form-group select, .form-group textarea {
  width: 100%;
  padding: 10px;
  border: 1px solid #cbd5e1;
  border-radius: 6px;
  font-family: inherit;
}
.hint {
  color: #94a3b8;
  font-size: 0.85rem;
  margin-top: 5px;
  display: block;
}
.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 20px;
}
.btn-cancel {
  background: #f0f0f0;
  border: none;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
}

.btn-confirm {
  background: #667eea;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
}

.btn-danger {
  background: #ff4d4f;
  color: white;
  border: none;
  padding: 10px 16px;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 500;
  width: 100%;
  transition: background 0.3s;
}

.btn-danger:hover {
  background: #ff7875;
}
</style>
