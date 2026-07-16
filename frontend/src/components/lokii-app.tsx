'use client';

import { useEffect, useMemo, useState, type ReactNode } from 'react';
import { useQuery } from '@tanstack/react-query';
import {
  Box,
  Button,
  Divider,
  IconButton,
  InputBase,
  MenuItem,
  Select,
  Stack,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  Tab,
  Tabs,
  Typography,
} from '@mui/material';
import SearchIcon from '@mui/icons-material/Search';
import MenuIcon from '@mui/icons-material/Menu';
import NotificationsNoneIcon from '@mui/icons-material/NotificationsNone';
import AddIcon from '@mui/icons-material/Add';
import BoltIcon from '@mui/icons-material/Bolt';
import ShieldOutlinedIcon from '@mui/icons-material/ShieldOutlined';
import TimelineIcon from '@mui/icons-material/Timeline';
import HubIcon from '@mui/icons-material/Hub';
import AssessmentOutlinedIcon from '@mui/icons-material/AssessmentOutlined';
import SettingsOutlinedIcon from '@mui/icons-material/SettingsOutlined';
import PlayCircleOutlineIcon from '@mui/icons-material/PlayCircleOutline';
import HealthAndSafetyOutlinedIcon from '@mui/icons-material/HealthAndSafetyOutlined';
import ChevronRightIcon from '@mui/icons-material/ChevronRight';

import { gateway, gatewayFirst } from '@/lib/api';
import { hydrateLokiiStore, useLokiiStore } from '@/lib/store';
import { investigations as mockInvestigations, timeline, health, type Module } from '@/lib/mock';
import { Kpi, Panel, Progress, StatusChip } from './ui';
import { useQueryClient } from '@tanstack/react-query';

type LiveInvestigation = {
  id?: string;
  investigation_id?: string;
  title?: string;
  severity?: string;
  status?: string;
  confidence?: number | { score?: number };
  threat?: string;
  customer?: string;
  updated?: string;
  mitre?: string;
  metadata?: { tenant_id?: string; updated_at?: string };
  hypotheses?: Array<{ pattern_name?: string; mitre_mapping?: { technique?: string } }>;
  evidence_summary?: { total?: number };
  related_entities?: unknown[];
};

const nav: { label: Module; icon: ReactNode }[] = [
  { label: 'Overview', icon: <BoltIcon /> },
  { label: 'Investigations', icon: <ShieldOutlinedIcon /> },
  { label: 'Attack Simulator', icon: <PlayCircleOutlineIcon /> },
  { label: 'Threat Intelligence', icon: <HubIcon /> },
  { label: 'Knowledge Platform', icon: <AssessmentOutlinedIcon /> },
  { label: 'MITRE ATT&CK', icon: <TimelineIcon /> },
  { label: 'System Health', icon: <HealthAndSafetyOutlinedIcon /> },
  { label: 'Settings', icon: <SettingsOutlinedIcon /> },
];

const severityTone = (severity: string) =>
  severity === 'Critical' || severity === 'critical'
    ? 'error'
    : severity === 'High' || severity === 'high'
      ? 'warning'
      : severity === 'Medium' || severity === 'medium'
        ? 'info'
        : 'success';

function normalizeInvestigation(item: LiveInvestigation) {
  const id = item.id ?? item.investigation_id ?? 'INV-UNKNOWN';
  const title = item.title ?? item.hypotheses?.[0]?.pattern_name ?? 'Investigation';
  const severity = String(item.severity ?? item.status ?? 'Medium');
  const status = String(item.status ?? 'Ready');
  const confidence = Number(item.confidence && typeof item.confidence === 'object' ? item.confidence.score ?? 0 : item.confidence ?? 62);
  const threat = item.threat ?? item.hypotheses?.[0]?.pattern_name ?? 'Account Takeover';
  const customer = item.customer ?? item.metadata?.tenant_id ?? 'demo-bank';
  const updated = item.updated ?? item.metadata?.updated_at ?? 'moments ago';
  const mitre = item.mitre ?? item.hypotheses?.[0]?.mitre_mapping?.technique ?? 'T1110';
  return { id, title, severity, status, confidence, threat, customer, updated, mitre, raw: item };
}

function GatewayStatus() {
  const healthQuery = useQuery({ queryKey: ['platform-health'], queryFn: gateway.health, refetchInterval: 15000 });
  const investigationQuery = useQuery({
    queryKey: ['gateway-investigations-status'],
    queryFn: () => gatewayFirst(gateway.investigations, mockInvestigations),
    refetchInterval: 15000,
  });

  const count = Array.isArray(investigationQuery.data) ? investigationQuery.data.length : 0;

  return (
    <Typography color="text.secondary" fontSize={10}>
      {healthQuery.isFetching
        ? 'Refreshing Gateway…'
        : healthQuery.isError
          ? 'Gateway fallback mode'
          : `Gateway connected · ${count} investigations`}
    </Typography>
  );
}

function Overview() {
  return (
    <Stack spacing={2}>
      <Stack direction="row" justifyContent="space-between" alignItems="center">
        <Box>
          <Typography variant="h5" fontWeight={800}>Platform overview</Typography>
          <Typography color="text.secondary" fontSize={12}>Real-time operational view · demo-ready</Typography>
        </Box>
        <Button variant="contained" startIcon={<PlayCircleOutlineIcon />} onClick={() => useLokiiStore.getState().setModule('Attack Simulator')}>
          Run attack scenario
        </Button>
      </Stack>

      <Box sx={{ display: 'grid', gridTemplateColumns: 'repeat(4,1fr)', gap: 1.5 }}>
        <Kpi label="Active investigations" value="24" detail="↑ 18% vs last 24h" />
        <Kpi label="Threat level" value="Elevated" detail="7 critical signals" tone="amber" />
        <Kpi label="Cases created" value="18" detail="100% immutable artifacts" tone="green" />
        <Kpi label="Execution queue" value="06" detail="2 awaiting approval" tone="blue" />
      </Box>

      <Box sx={{ display: 'grid', gridTemplateColumns: '1.35fr 1fr 1fr', gap: 1.5 }}>
        <Panel title="Live investigation timeline" action={<StatusChip label="LIVE" color="success" />}>
          <Stack spacing={1.5}>
            {timeline.slice(0, 6).map(([time, type, text, service]) => (
              <Stack direction="row" spacing={1.5} key={time as string}>
                <Typography className="mono" color="text.secondary" sx={{ fontSize: 11, width: 62 }}>{time as string}</Typography>
                <Box sx={{ width: 7, height: 7, borderRadius: '50%', bgcolor: type === 'THREAT' ? '#ef4444' : '#38bdf8', mt: 0.6, boxShadow: '0 0 0 3px #1e3a5f' }} />
                <Box>
                  <Typography fontSize={12} fontWeight={650}>{text as string}</Typography>
                  <Typography color="text.secondary" fontSize={11}>{service as string}</Typography>
                </Box>
              </Stack>
            ))}
          </Stack>
        </Panel>

        <Panel title="MITRE coverage">
          <Typography fontSize={33} fontWeight={800}>72%</Typography>
          <Typography color="text.secondary" fontSize={12}>48 of 66 techniques observed</Typography>
          <Progress value={72} />
        </Panel>

        <Panel title="Gateway status">
          <GatewayStatus />
        </Panel>
      </Box>
    </Stack>
  );
}

function Investigations() {
  const { selectInvestigation } = useLokiiStore();
  const [q, setQ] = useState('');
  const liveQuery = useQuery({
    queryKey: ['gateway-investigations-table'],
    queryFn: () => gatewayFirst(gateway.investigations, mockInvestigations),
    refetchInterval: 15000,
  });

  const rows = useMemo(() => {
    const source = Array.isArray(liveQuery.data) ? liveQuery.data : mockInvestigations;
    return source
      .map((item: any) => normalizeInvestigation(item))
      .filter((item) => (item.id + item.title + item.customer).toLowerCase().includes(q.toLowerCase()));
  }, [liveQuery.data, q]);

  return (
    <Stack spacing={2}>
      <Stack direction="row" justifyContent="space-between">
        <Box>
          <Typography variant="h5" fontWeight={800}>Investigations</Typography>
          <Typography color="text.secondary" fontSize={12}>{liveQuery.isError ? 'Showing fallback investigations' : 'Live gateway investigations · demo-ready'}</Typography>
        </Box>
        <Button variant="contained" startIcon={<AddIcon />} onClick={() => useLokiiStore.getState().setModule('Attack Simulator')}>
          New investigation
        </Button>
      </Stack>

      <Panel>
        <Stack direction="row" spacing={1} mb={2}>
          <InputBase
            value={q}
            onChange={(e) => setQ(e.target.value)}
            placeholder="Search investigations, customers, threats…"
            startAdornment={<SearchIcon sx={{ color: '#64748b', mr: 1 }} />}
            sx={{ px: 1.5, py: 0.5, border: '1px solid #334155', borderRadius: 1, flex: 1, fontSize: 13 }}
          />
          <Select size="small" defaultValue="all" sx={{ minWidth: 125, fontSize: 12 }}>
            <MenuItem value="all">All severities</MenuItem>
            <MenuItem value="critical">Critical</MenuItem>
          </Select>
          <Button variant="outlined">Filters</Button>
        </Stack>

        <Table size="small">
          <TableHead>
            <TableRow>
              {['Investigation ID', 'Severity', 'Status', 'Confidence', 'MITRE', 'Threat', 'Customer', 'Updated', ''].map((h) => (
                <TableCell key={h}>{h}</TableCell>
              ))}
            </TableRow>
          </TableHead>
          <TableBody>
            {rows.map((item) => (
              <TableRow hover key={item.id} onClick={() => selectInvestigation(item.id)} sx={{ cursor: 'pointer' }}>
                <TableCell>
                  <Typography fontSize={12} fontWeight={700}>{item.id}</Typography>
                  <Typography fontSize={11} color="text.secondary">{item.title}</Typography>
                </TableCell>
                <TableCell><StatusChip label={item.severity} color={severityTone(item.severity) as any} /></TableCell>
                <TableCell>
                  <StatusChip
                    label={item.status}
                    color={item.status.toLowerCase().includes('completed') || item.status.toLowerCase().includes('ready') ? 'success' : item.status.toLowerCase().includes('ai') ? 'info' : 'warning'}
                  />
                </TableCell>
                <TableCell>
                  <Stack direction="row" spacing={1} alignItems="center">
                    <Progress value={Math.min(100, item.confidence)} color={item.confidence > 90 ? '#ef4444' : '#2563eb'} />
                    <Typography fontSize={11}>{item.confidence}%</Typography>
                  </Stack>
                </TableCell>
                <TableCell>{item.mitre}</TableCell>
                <TableCell>{item.threat}</TableCell>
                <TableCell>{item.customer}</TableCell>
                <TableCell>{item.updated}</TableCell>
                <TableCell><ChevronRightIcon fontSize="small" /></TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </Panel>
    </Stack>
  );
}

function RelationshipGraph() {
  const nodes = [
    ['User', '22%', '32%', '#38bdf8'],
    ['IP address', '66%', '22%', '#f59e0b'],
    ['Account', '45%', '58%', '#a78bfa'],
    ['Device', '76%', '64%', '#22c55e'],
    ['MITRE T1110', '23%', '78%', '#ef4444'],
  ] as const;

  return (
    <Box className="grid-bg" sx={{ height: 390, borderRadius: 1, position: 'relative', overflow: 'hidden' }}>
      <Typography sx={{ position: 'absolute', top: 18, left: 18, fontSize: 13, fontWeight: 700 }}>Relationship explorer</Typography>
      {nodes.map(([name, left, top, color]) => (
        <Box key={name} sx={{ position: 'absolute', left, top, p: 1.5, border: `1px solid ${color}`, borderRadius: 2, bgcolor: '#17243a', boxShadow: `0 0 24px ${color}33` }}>
          <Typography fontSize={11} color={color} fontWeight={700}>{name}</Typography>
          <Typography fontSize={10} color="text.secondary">linked entity</Typography>
        </Box>
      ))}
      <svg width="100%" height="100%" style={{ position: 'absolute', inset: 0, pointerEvents: 'none' }}>
        <line x1="28%" y1="38%" x2="70%" y2="28%" stroke="#475569" />
        <line x1="70%" y1="28%" x2="50%" y2="64%" stroke="#475569" />
        <line x1="50%" y1="64%" x2="28%" y2="82%" stroke="#475569" />
        <line x1="50%" y1="64%" x2="79%" y2="68%" stroke="#475569" />
      </svg>
    </Box>
  );
}

function WorkspaceCards({ items }: { items: string[] }) {
  return (
    <Box sx={{ display: 'grid', gridTemplateColumns: 'repeat(3,1fr)', gap: 1.5 }}>
      {items.map((item, index) => (
        <Panel key={item} title={item}>
          <Typography fontSize={12} color="text.secondary">
            {index % 2 ? 'Traceable artifact linked to CaseFile v1.' : 'AI-generated insight ready for analyst review.'}
          </Typography>
          <Button size="small" sx={{ mt: 2 }}>Open artifact <ChevronRightIcon fontSize="small" /></Button>
        </Panel>
      ))}
    </Box>
  );
}

function Workspace() {
  const { selectedInvestigation } = useLokiiStore();
  const liveQuery = useQuery({
    queryKey: ['gateway-investigations-workspace'],
    queryFn: () => gatewayFirst(gateway.investigations, mockInvestigations),
    refetchInterval: 15000,
  });

  const source = Array.isArray(liveQuery.data) ? liveQuery.data : mockInvestigations;
  const item = source.map((entry: any) => normalizeInvestigation(entry)).find((entry) => entry.id === selectedInvestigation) ?? normalizeInvestigation(source[0] as any);

  const [tab, setTab] = useState(0);
  const tabs = ['Timeline', 'Evidence', 'Relationships', 'Case Intelligence', 'AI Reports', 'Response', 'Audit'];

  return (
    <Stack spacing={2}>
      <Stack direction="row" justifyContent="space-between">
        <Box>
          <Stack direction="row" spacing={1} alignItems="center">
            <Typography variant="h5" fontWeight={800}>{item.id}</Typography>
            <StatusChip label={item.severity} color={severityTone(item.severity) as any} />
          </Stack>
          <Typography color="text.secondary" fontSize={12}>{item.title} · {item.customer} · correlation <span className="mono">cor-9e41d</span></Typography>
        </Box>
        <Stack direction="row" spacing={1}>
          <Button variant="outlined">Export CaseFile</Button>
          <Button variant="contained" color="error">Escalate</Button>
        </Stack>
      </Stack>

      <Panel>
        <Tabs value={tab} onChange={(_, value) => setTab(value)} variant="scrollable" sx={{ borderBottom: '1px solid #334155', mb: 2 }}>
          {tabs.map((tabName) => <Tab key={tabName} label={tabName} />)}
        </Tabs>

        {tab === 0 && (
          <Stack spacing={2}>
            {timeline.map(([time, type, text, service]) => (
              <Stack direction="row" spacing={2} key={time as string}>
                <Typography className="mono" color="text.secondary" fontSize={12} width={70}>{time as string}</Typography>
                <Box sx={{ width: 10, height: 10, borderRadius: '50%', bgcolor: type === 'THREAT' ? '#ef4444' : '#0ea5e9', mt: 0.5 }} />
                <Box flex={1}>
                  <Stack direction="row" justifyContent="space-between">
                    <Typography fontSize={13} fontWeight={700}>{text as string}</Typography>
                    <StatusChip label={type as string} />
                  </Stack>
                  <Typography fontSize={11} color="text.secondary">{service as string} · event accepted · trace <span className="mono">tr-7c4b91</span></Typography>
                </Box>
              </Stack>
            ))}
          </Stack>
        )}

        {tab === 1 && (
          <Box className="grid-bg" sx={{ p: 3, borderRadius: 1, minHeight: 300 }}>
            <Typography fontSize={13} fontWeight={700}>Evidence explorer</Typography>
            <Typography color="text.secondary" fontSize={12} mt={1}>
              {item.confidence}% confidence · {item.raw.evidence_summary?.total ?? 3} evidence items · {item.mitre}
            </Typography>
            <Box sx={{ mt: 3, display: 'grid', gridTemplateColumns: 'repeat(4,1fr)', gap: 1.5 }}>
              {['Authentication', 'Device', 'Transaction', 'Graph'].map((label, index) => (
                <Panel key={label} title={label}>
                  <Typography fontSize={22} fontWeight={800}>{index === 3 ? `${item.raw.related_entities?.length ?? 0}` : `${Math.max(1, Math.round(item.confidence))}%`}</Typography>
                  <Typography color="text.secondary" fontSize={11}>confidence coverage</Typography>
                </Panel>
              ))}
            </Box>
          </Box>
        )}

        {tab === 2 && <RelationshipGraph />}
        {tab === 3 && <WorkspaceCards items={['Case summary', 'Entity map', 'Open indicators']} />}
        {tab === 4 && <WorkspaceCards items={['AI summary', 'AI narrative', 'AI evidence notes']} />}
        {tab === 5 && <WorkspaceCards items={['Approve step-up alert', 'Contain account', 'Notify fraud team']} />}
        {tab === 6 && <WorkspaceCards items={['Audit log', 'Case mutation history', 'Immutable diff']} />}
      </Panel>
    </Stack>
  );
}

function Simulator() {
  const [scenario, setScenario] = useState('Credential Stuffing');
  const [running, setRunning] = useState(false);
  const [demoStatus, setDemoStatus] = useState('');
  const [trace, setTrace] = useState<string[]>([]);
  const queryClient = useQueryClient();
  const { setModule, selectInvestigation } = useLokiiStore();
  const investigationsQuery = useQuery({
    queryKey: ['gateway-investigations-simulator'],
    queryFn: () => gatewayFirst(gateway.investigations, mockInvestigations),
    refetchInterval: 15000,
  });

  useEffect(() => {
    hydrateLokiiStore();
    if (typeof window !== 'undefined') {
      setScenario(window.localStorage.getItem('lokii-simulator-scenario') ?? 'Credential Stuffing');
      setDemoStatus(window.localStorage.getItem('lokii-simulator-status') ?? '');
    }
  }, []);

  const saveScenario = (value: string) => {
    setScenario(value);
    if (typeof window !== 'undefined') {
      window.localStorage.setItem('lokii-simulator-scenario', value);
    }
  };

  const saveDemoStatus = (value: string) => {
    setDemoStatus(value);
    if (typeof window !== 'undefined') {
      window.localStorage.setItem('lokii-simulator-status', value);
    }
  };

  const appendTrace = (message: string) => {
    setTrace((current) => [...current, message]);
  };

  const handleRunScenario = async () => {
    setTrace([]);
    appendTrace('Entering handleRunScenario');
    setRunning(true);
    saveDemoStatus('Starting scenario…');
    try {
      appendTrace('Sending POST request');
      const result = await gateway.runScenario(scenario);
      appendTrace('Response received');
      const simulationId = result?.simulation_id ? `Simulation ${result.simulation_id}` : 'Scenario started';
      appendTrace(`Simulation ID: ${result?.simulation_id ?? 'missing'}`);
      const publishStatus = result?.demo_candidate_status === 'published' ? 'demo candidate published' : 'demo candidate queued';
      saveDemoStatus(`${simulationId} · ${publishStatus}`);

      appendTrace('Polling started');
      const initialInvestigations = Array.isArray(investigationsQuery.data) ? investigationsQuery.data : [];
      let foundInvestigation: any = null;

      for (let attempt = 0; attempt < 10; attempt += 1) {
        const latest = await gateway.investigations();
        await queryClient.invalidateQueries({ queryKey: ['gateway-investigations-home'] });
        await queryClient.invalidateQueries({ queryKey: ['gateway-investigations-status'] });
        await queryClient.invalidateQueries({ queryKey: ['gateway-investigations-table'] });
        await queryClient.invalidateQueries({ queryKey: ['gateway-investigations-workspace'] });
        await queryClient.invalidateQueries({ queryKey: ['gateway-investigations-simulator'] });

        const latestList = Array.isArray(latest) ? latest : [];
        foundInvestigation = latestList.find((item: any) => !initialInvestigations.some((original: any) => (original.id ?? original.investigation_id) === (item.id ?? item.investigation_id))) ?? latestList[0] ?? null;
        if (foundInvestigation) {
          appendTrace('Investigation found');
          break;
        }

        await new Promise((resolve) => setTimeout(resolve, 1000));
      }

      if (foundInvestigation) {
        const nextId = foundInvestigation.id ?? foundInvestigation.investigation_id;
        if (nextId) {
          selectInvestigation(nextId);
        }
        appendTrace('State updated');
        appendTrace('React re-render');
        setModule('Investigation Workspace');
        appendTrace('Workspace opened');
      }
    } catch {
      saveDemoStatus('Gateway fallback mode · scenario request failed');
      appendTrace('Execution stopped');
    } finally {
      setRunning(false);
    }
  };

  return (
    <Stack spacing={2}>
      <Typography variant="h5" fontWeight={800}>Attack simulator</Typography>
      <Typography color="text.secondary" fontSize={12}>Launch a deterministic scenario and watch the autonomous pipeline progress.</Typography>

      <Panel>
        <Typography fontSize={13} fontWeight={700} mb={1.5}>Choose scenario</Typography>
        <Stack direction="row" spacing={1} flexWrap="wrap" useFlexGap>
          {['Credential Stuffing', 'Account Takeover', 'Password Spray', 'Money Mule', 'Insider Threat', 'Ransomware', 'Quantum Attack'].map((value) => (
            <Button key={value} variant={scenario === value ? 'contained' : 'outlined'} onClick={() => saveScenario(value)}>{value}</Button>
          ))}
        </Stack>

        <Divider sx={{ my: 2 }} />

        <Stack direction="row" justifyContent="space-between" alignItems="center">
          <Box>
            <Typography fontWeight={700}>{running ? 'Scenario running' : 'Ready to simulate'} · {scenario}</Typography>
            <Typography color="text.secondary" fontSize={12}>{running ? 'Events are moving through Kafka and downstream services.' : demoStatus || 'Only this action is required from the analyst.'}</Typography>
          </Box>
          <Button variant="contained" size="large" startIcon={<PlayCircleOutlineIcon />} onClick={handleRunScenario} disabled={running}>
            {running ? 'Running…' : 'Run scenario'}
          </Button>
        </Stack>
      </Panel>

      {(trace.length > 0 || running) && (
        <Panel title="Execution trace" action={<StatusChip label={running ? 'LIVE' : 'DONE'} color={running ? 'success' : 'info'} />}>
          <Stack spacing={0.75}>
            {trace.map((entry) => (
              <Typography key={entry} fontSize={12} color="text.secondary">{entry}</Typography>
            ))}
          </Stack>
        </Panel>
      )}

      {running && (
        <Panel title="Pipeline progress" action={<StatusChip label="LIVE" color="success" />}>
          <Stack spacing={1.5}>
            {['Simulator', 'Ingestion', 'Evidence Intelligence', 'Threat Intelligence', 'Investigation', 'Case Builder', 'AI Reports', 'Execution', 'ServiceNow'].map((label, index) => (
              <Stack direction="row" spacing={1.5} alignItems="center" key={label}>
                <Box sx={{ width: 22, height: 22, borderRadius: '50%', bgcolor: index < 4 ? '#2563eb' : '#1e293b', border: '1px solid #475569', display: 'grid', placeItems: 'center', fontSize: 11 }}>
                  {index < 4 ? '✓' : index + 1}
                </Box>
                <Typography fontSize={12} flex={1}>{label}</Typography>
                <Typography color="text.secondary" fontSize={11}>{index < 4 ? 'completed' : index === 4 ? 'processing' : 'queued'}</Typography>
                <Progress value={index < 4 ? 100 : Math.max(10, 100 - index * 11)} />
              </Stack>
            ))}
          </Stack>
        </Panel>
      )}
    </Stack>
  );
}

function Health() {
  return (
    <Stack spacing={2}>
      <Typography variant="h5" fontWeight={800}>System health</Typography>
      <Typography color="text.secondary" fontSize={12}>Operational status across Lokii dependencies and event infrastructure.</Typography>
      <Box sx={{ display: 'grid', gridTemplateColumns: 'repeat(3,1fr)', gap: 1.5 }}>
        {health.map(([name, status, latency]) => (
          <Panel key={name as string}>
            <Stack direction="row" justifyContent="space-between">
              <Typography fontWeight={700}>{name as string}</Typography>
              <StatusChip label={status as string} color={status === 'Healthy' ? 'success' : 'warning'} />
            </Stack>
            <Typography sx={{ fontSize: 26, fontWeight: 800, mt: 2 }}>{latency as string}</Typography>
            <Typography color="text.secondary" fontSize={11}>current response latency</Typography>
            <Progress value={status === 'Healthy' ? 92 : 58} color={status === 'Healthy' ? '#22c55e' : '#f59e0b'} />
          </Panel>
        ))}
      </Box>
    </Stack>
  );
}

function Generic({ module }: { module: Module }) {
  return (
    <Stack spacing={2}>
      <Typography variant="h5" fontWeight={800}>{module}</Typography>
      <Typography color="text.secondary" fontSize={12}>Investigation-centric intelligence and operational controls for your SOC team.</Typography>
      <Box sx={{ display: 'grid', gridTemplateColumns: 'repeat(3,1fr)', gap: 1.5 }}>
        {['Threat actors', 'Recent intelligence', 'Detection coverage', 'Policy library', 'Pattern history', 'Analyst actions'].map((label, index) => (
          <Panel title={label} key={label}>
            <Typography fontSize={26} fontWeight={800}>{[12, 48, 72, 26, 184, 9][index]}</Typography>
            <Typography color="text.secondary" fontSize={11}>updated moments ago</Typography>
          </Panel>
        ))}
      </Box>
    </Stack>
  );
}

export default function LokiiApp() {
  const { module, sidebarOpen, toggleSidebar, setModule, notifications } = useLokiiStore();
  const liveQuery = useQuery({ queryKey: ['gateway-investigations-home'], queryFn: () => gatewayFirst(gateway.investigations, mockInvestigations), refetchInterval: 15000 });
  const investigationCount = Array.isArray(liveQuery.data) ? liveQuery.data.length : mockInvestigations.length;

  return (
    <Box sx={{ display: 'flex', minHeight: '100vh', bgcolor: '#0b1220' }}>
      <Box component="aside" sx={{ width: sidebarOpen ? 238 : 68, transition: 'width .2s', borderRight: '1px solid #23324a', bgcolor: '#0f192b', flexShrink: 0, display: 'flex', flexDirection: 'column' }}>
        <Stack direction="row" alignItems="center" spacing={1.2} sx={{ p: 2, height: 64 }}>
          <Box sx={{ width: 30, height: 30, borderRadius: 1, bgcolor: '#2563eb', display: 'grid', placeItems: 'center', fontWeight: 900, fontSize: 18 }}>L</Box>
          {sidebarOpen && (
            <Box>
              <Typography fontWeight={900} fontSize={17} letterSpacing={1}>Lokii</Typography>
              <Typography color="text.secondary" fontSize={9} letterSpacing={1}>SECURITY OPERATIONS</Typography>
            </Box>
          )}
        </Stack>
        <Divider />
        <Stack spacing={0.5} sx={{ p: 1, flex: 1 }}>
          {nav.map((item) => (
            <Button
              key={item.label}
              onClick={() => setModule(item.label)}
              startIcon={item.icon}
              sx={{
                justifyContent: sidebarOpen ? 'flex-start' : 'center',
                minWidth: 0,
                px: 1.5,
                py: 1.1,
                color: module === item.label ? '#fff' : '#94a3b8',
                bgcolor: module === item.label ? '#1d4ed833' : 'transparent',
                '&:hover': { bgcolor: '#1e293b' },
                '& .MuiButton-startIcon': { margin: sidebarOpen ? '0 10px 0 0' : 0 },
              }}
            >
              {sidebarOpen && item.label}
            </Button>
          ))}
        </Stack>
        {sidebarOpen && (
          <Box sx={{ p: 1.5, m: 1, border: '1px solid #334155', borderRadius: 1, bgcolor: '#17243a' }}>
            <Typography fontSize={10} color="text.secondary">PLATFORM STATUS</Typography>
            <Stack direction="row" spacing={1} mt={1} alignItems="center">
              <Box sx={{ width: 7, height: 7, borderRadius: '50%', bgcolor: '#22c55e' }} />
              <Typography fontSize={11}>All systems operational</Typography>
            </Stack>
          </Box>
        )}
      </Box>

      <Box component="main" sx={{ flex: 1, minWidth: 0 }}>
        <Stack component="header" direction="row" alignItems="center" spacing={2} sx={{ height: 64, p: '0 24px', borderBottom: '1px solid #23324a', bgcolor: '#0f192b' }}>
          <IconButton onClick={toggleSidebar} sx={{ color: '#94a3b8' }}><MenuIcon /></IconButton>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, px: 1.5, py: 0.75, border: '1px solid #334155', borderRadius: 1, flex: 1, maxWidth: 360 }}>
            <SearchIcon sx={{ color: '#64748b' }} />
            <Typography color="text.secondary" fontSize={12}>Search investigations, cases, threats…</Typography>
          </Box>
          <Box sx={{ flex: 1 }} />
          <GatewayStatus />
          <IconButton sx={{ color: '#94a3b8' }}><NotificationsNoneIcon /></IconButton>
          <Box sx={{ width: 8, height: 8, borderRadius: '50%', bgcolor: '#ef4444', ml: -1.5, mt: -1.5 }}>{notifications > 0 ? notifications : null}</Box>
        </Stack>

        <Box sx={{ p: 3 }}>
          {module === 'Overview' && <Overview />}
          {module === 'Investigations' && <Investigations />}
          {module === 'Attack Simulator' && <Simulator />}
          {module === 'System Health' && <Health />}
          {module === 'Investigation Workspace' && <Workspace />}
          {['Threat Intelligence', 'Knowledge Platform', 'MITRE ATT&CK', 'Settings'].includes(module) && <Generic module={module} />}
        </Box>

        <Box sx={{ p: 2, pt: 0, color: '#64748b', fontSize: 11 }}>
          Gateway investigations visible: {investigationCount}
        </Box>
      </Box>
    </Box>
  );
}
