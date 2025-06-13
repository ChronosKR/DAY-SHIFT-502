import express from 'express';
import { WebSocketServer } from 'ws';
import { createServer } from 'http';
import cors from 'cors';
import { marked } from 'marked';
import { readFileSync, existsSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const app = express();
const server = createServer(app);
const wss = new WebSocketServer({ server });

// Middleware
app.use(cors());
app.use(express.json());
app.use(express.static(join(__dirname, 'plc_scada_lab', 'frontend')));

// MODBUS simulation data
let modbusRegisters = {
  coils: new Array(100).fill(false),
  discreteInputs: new Array(100).fill(false),
  holdingRegisters: new Array(100).fill(0),
  inputRegisters: new Array(100).fill(0)
};

// Lessons data
const lessons = [
  {
    id: 1,
    title: "Introduction to PLCs",
    description: "Learn the basics of Programmable Logic Controllers",
    content: "intro"
  },
  {
    id: 2,
    title: "MODBUS Protocol",
    description: "Understanding MODBUS communication protocol",
    content: "modbus"
  },
  {
    id: 3,
    title: "Ladder Logic Programming",
    description: "Programming PLCs with ladder logic",
    content: "ladder_logic"
  },
  {
    id: 4,
    title: "HMI and SCADA Systems",
    description: "Human Machine Interface and SCADA concepts",
    content: "hmi_scada"
  },
  {
    id: 5,
    title: "Industrial Networking",
    description: "Networking in industrial automation",
    content: "networking"
  }
];

// API Routes
app.get('/api/lessons', (req, res) => {
  res.json(lessons);
});

app.get('/api/lessons/:id', (req, res) => {
  const lessonId = parseInt(req.params.id);
  const lesson = lessons.find(l => l.id === lessonId);
  
  if (!lesson) {
    return res.status(404).json({ error: 'Lesson not found' });
  }

  // Try to load markdown content
  const markdownPath = join(__dirname, 'plc_scada_lab', 'docs', `0${lessonId}_${lesson.content}.md`);
  let content = 'Content not available';
  
  if (existsSync(markdownPath)) {
    try {
      const markdownContent = readFileSync(markdownPath, 'utf8');
      content = marked(markdownContent);
    } catch (error) {
      console.error('Error reading markdown file:', error);
    }
  }

  res.json({
    ...lesson,
    content: content
  });
});

// MODBUS API endpoints
app.get('/api/modbus/registers', (req, res) => {
  res.json(modbusRegisters);
});

app.post('/api/modbus/write-coil', (req, res) => {
  const { address, value } = req.body;
  
  if (address >= 0 && address < modbusRegisters.coils.length) {
    modbusRegisters.coils[address] = Boolean(value);
    
    // Broadcast update to all connected WebSocket clients
    wss.clients.forEach(client => {
      if (client.readyState === 1) { // WebSocket.OPEN
        client.send(JSON.stringify({
          type: 'modbus_update',
          data: { address, value: Boolean(value), register_type: 'coil' }
        }));
      }
    });
    
    res.json({ success: true, address, value: Boolean(value) });
  } else {
    res.status(400).json({ error: 'Invalid address' });
  }
});

app.post('/api/modbus/write-register', (req, res) => {
  const { address, value } = req.body;
  
  if (address >= 0 && address < modbusRegisters.holdingRegisters.length) {
    modbusRegisters.holdingRegisters[address] = parseInt(value);
    
    // Broadcast update to all connected WebSocket clients
    wss.clients.forEach(client => {
      if (client.readyState === 1) { // WebSocket.OPEN
        client.send(JSON.stringify({
          type: 'modbus_update',
          data: { address, value: parseInt(value), register_type: 'holding_register' }
        }));
      }
    });
    
    res.json({ success: true, address, value: parseInt(value) });
  } else {
    res.status(400).json({ error: 'Invalid address' });
  }
});

// WebSocket handling
wss.on('connection', (ws) => {
  console.log('New WebSocket connection');
  
  // Send current state to new client
  ws.send(JSON.stringify({
    type: 'initial_state',
    data: modbusRegisters
  }));
  
  ws.on('message', (message) => {
    try {
      const data = JSON.parse(message.toString());
      console.log('Received WebSocket message:', data);
      
      // Handle different message types
      switch (data.type) {
        case 'ping':
          ws.send(JSON.stringify({ type: 'pong' }));
          break;
        default:
          console.log('Unknown message type:', data.type);
      }
    } catch (error) {
      console.error('Error parsing WebSocket message:', error);
    }
  });
  
  ws.on('close', () => {
    console.log('WebSocket connection closed');
  });
});

// Serve the main application
app.get('/', (req, res) => {
  res.sendFile(join(__dirname, 'plc_scada_lab', 'frontend', 'index.html'));
});

const PORT = process.env.PORT || 8000;
server.listen(PORT, () => {
  console.log(`🏭 PLC SCADA Lab server running on http://localhost:${PORT}`);
  console.log('📚 Access the training modules at the root URL');
});