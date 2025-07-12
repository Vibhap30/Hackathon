// import React, { useRef, useEffect } from 'react';
// import * as d3 from 'd3';

// // Define the participant type as used in the parent
// interface NetworkParticipant {
//   name: string;
//   type: string;
//   status: string;
//   provider_count: number;
//   active_offers: number;
//   coverage_area: string[];
//   subscriber_id: string;
// }

// interface D3NetworkNode extends NetworkParticipant {
//   id: string;
//   x?: number;
//   y?: number;
//   vx?: number;
//   vy?: number;
//   fx?: number | null;
//   fy?: number | null;
// }

// interface LiveTransaction {
//   id: string;
//   fromNetwork: string;
//   toNetwork: string;
//   status: string;
//   action: string;
//   energyAmount: number;
//   price: number;
//   timestamp: string;
// }

// interface D3Link extends LiveTransaction {
//   source: string | D3NetworkNode;
//   target: string | D3NetworkNode;
// }

// interface BecknNetworkGraphProps {
//   participants: NetworkParticipant[];
//   transactions: LiveTransaction[];
// }

// const BecknNetworkGraph: React.FC<BecknNetworkGraphProps> = ({ participants, transactions }) => {
//   const svgRef = useRef<SVGSVGElement | null>(null);

//   useEffect(() => {
//     if (!svgRef.current) return;
//     const width = 800;
//     const height = 500;
//     const svg = d3.select(svgRef.current);
//     svg.selectAll('*').remove();

//     // Use fallback data if no participants are provided
//     const fallbackParticipants: NetworkParticipant[] = [
//       {
//         name: 'PowerShare Platform',
//         type: 'BAP',
//         status: 'SUBSCRIBED',
//         provider_count: 15,
//         active_offers: 42,
//         coverage_area: ['Mumbai', 'Delhi', 'Bangalore'],
//         subscriber_id: 'powershare.energy.platform'
//       },
//       {
//         name: 'Green Energy Hub',
//         type: 'BPP',
//         status: 'SUBSCRIBED', 
//         provider_count: 8,
//         active_offers: 23,
//         coverage_area: ['Pune', 'Chennai'],
//         subscriber_id: 'green.energy.hub'
//       },
//       {
//         name: 'Solar Trade Network',
//         type: 'BPP',
//         status: 'SUBSCRIBED',
//         provider_count: 12,
//         active_offers: 31,
//         coverage_area: ['Hyderabad', 'Kolkata'],
//         subscriber_id: 'solar.trade.network'
//       },
//       {
//         name: 'Wind Power Co',
//         type: 'BPP',
//         status: 'ACTIVE',
//         provider_count: 6,
//         active_offers: 18,
//         coverage_area: ['Gujarat', 'Rajasthan'],
//         subscriber_id: 'wind.power.co'
//       },
//       {
//         name: 'Hydro Energy Ltd',
//         type: 'BPP',
//         status: 'SUBSCRIBED',
//         provider_count: 4,
//         active_offers: 12,
//         coverage_area: ['Kerala', 'Karnataka'],
//         subscriber_id: 'hydro.energy.ltd'
//       },
//       {
//         name: 'Metro Energy BAP',
//         type: 'BAP',
//         status: 'SUBSCRIBED',
//         provider_count: 20,
//         active_offers: 55,
//         coverage_area: ['NCR', 'Gurgaon'],
//         subscriber_id: 'metro.energy.bap'
//       },
//       {
//         name: 'Rural Power Hub',
//         type: 'BG',
//         status: 'ACTIVE',
//         provider_count: 25,
//         active_offers: 68,
//         coverage_area: ['Bihar', 'UP', 'MP'],
//         subscriber_id: 'rural.power.hub'
//       },
//       {
//         name: 'Clean Energy Network',
//         type: 'BPP',
//         status: 'SUBSCRIBED',
//         provider_count: 10,
//         active_offers: 28,
//         coverage_area: ['Tamil Nadu', 'Andhra Pradesh'],
//         subscriber_id: 'clean.energy.network'
//       },
//       {
//         name: 'Smart Grid Solutions',
//         type: 'BAP',
//         status: 'ACTIVE',
//         provider_count: 18,
//         active_offers: 45,
//         coverage_area: ['Haryana', 'Punjab'],
//         subscriber_id: 'smart.grid.solutions'
//       },
//       {
//         name: 'Renewable Energy Corp',
//         type: 'BPP',
//         status: 'SUBSCRIBED',
//         provider_count: 14,
//         active_offers: 38,
//         coverage_area: ['Odisha', 'Jharkhand'],
//         subscriber_id: 'renewable.energy.corp'
//       },
//       {
//         name: 'Energy Gateway',
//         type: 'BG',
//         status: 'SUBSCRIBED',
//         provider_count: 30,
//         active_offers: 82,
//         coverage_area: ['West Bengal', 'Assam'],
//         subscriber_id: 'energy.gateway'
//       },
//       {
//         name: 'Solar City Network',
//         type: 'BPP',
//         status: 'ACTIVE',
//         provider_count: 7,
//         active_offers: 19,
//         coverage_area: ['Goa', 'Maharashtra'],
//         subscriber_id: 'solar.city.network'
//       },
//       {
//         name: 'Power Trading Hub',
//         type: 'BAP',
//         status: 'SUBSCRIBED',
//         provider_count: 22,
//         active_offers: 61,
//         coverage_area: ['Himachal Pradesh', 'Uttarakhand'],
//         subscriber_id: 'power.trading.hub'
//       }
//     ];

//     const fallbackTransactions: LiveTransaction[] = [
//       {
//         id: 'tx_demo_1',
//         fromNetwork: 'PowerShare Platform',
//         toNetwork: 'Green Energy Hub',
//         status: 'completed',
//         action: 'init',
//         energyAmount: 50,
//         price: 4.25,
//         timestamp: new Date().toISOString()
//       },
//       {
//         id: 'tx_demo_2',
//         fromNetwork: 'Solar Trade Network',
//         toNetwork: 'PowerShare Platform',
//         status: 'completed',
//         action: 'confirm',
//         energyAmount: 75,
//         price: 3.80,
//         timestamp: new Date().toISOString()
//       },
//       {
//         id: 'tx_demo_3',
//         fromNetwork: 'Wind Power Co',
//         toNetwork: 'Metro Energy BAP',
//         status: 'pending',
//         action: 'init',
//         energyAmount: 35,
//         price: 5.10,
//         timestamp: new Date().toISOString()
//       },
//       {
//         id: 'tx_demo_4',
//         fromNetwork: 'Clean Energy Network',
//         toNetwork: 'Smart Grid Solutions',
//         status: 'completed',
//         action: 'select',
//         energyAmount: 60,
//         price: 3.95,
//         timestamp: new Date().toISOString()
//       },
//       {
//         id: 'tx_demo_5',
//         fromNetwork: 'Energy Gateway',
//         toNetwork: 'Renewable Energy Corp',
//         status: 'pending',
//         action: 'confirm',
//         energyAmount: 90,
//         price: 4.50,
//         timestamp: new Date().toISOString()
//       },
//       {
//         id: 'tx_demo_6',
//         fromNetwork: 'Power Trading Hub',
//         toNetwork: 'Solar City Network',
//         status: 'completed',
//         action: 'init',
//         energyAmount: 25,
//         price: 5.75,
//         timestamp: new Date().toISOString()
//       }
//     ];

//     // Use provided data or fallback
//     const activeParticipants = participants && participants.length > 0 ? participants : fallbackParticipants;
//     const activeTransactions = transactions && transactions.length > 0 ? transactions : fallbackTransactions;

//     // Prepare nodes and links
//     const nodes: D3NetworkNode[] = activeParticipants.map(p => ({ id: p.name, ...p }));
//     const links: D3Link[] = activeTransactions.map(t => ({
//       source: t.fromNetwork,
//       target: t.toNetwork,
//       ...t
//     }));

//     // Force simulation with better spaced layout
//     const simulation = d3.forceSimulation<D3NetworkNode>(nodes)
//       .force('link', d3.forceLink<D3NetworkNode, D3Link>(links)
//         .id((d: any) => d.id)
//         .distance(160) // Increased for more spacing between nodes
//         .strength(0.6) // Moderate link force
//       )
//       .force('charge', d3.forceManyBody().strength(-400)) // More repulsion for better spacing
//       .force('center', d3.forceCenter(width / 2, height / 2))
//       .force('collide', d3.forceCollide(45)) // Larger collision radius for better spacing
//       .force('x', d3.forceX(width / 2).strength(0.08)) // Gentler pull towards center X
//       .force('y', d3.forceY(height / 2).strength(0.08)); // Gentler pull towards center Y

//     // Draw links (edges) with enhanced visual appeal and blinking animation
//     const link = svg.append('g')
//       .attr('stroke', '#aaa')
//       .attr('stroke-width', 4) // Increased from 3
//       .selectAll('line')
//       .data(links)
//       .enter().append('line')
//       .attr('stroke', (d: D3Link) => d.action === 'init' ? '#f59e42' : '#38bdf8')
//       .attr('stroke-dasharray', '5,5') // Add dashed pattern for visual appeal
//       .attr('marker-end', 'url(#arrow)')
//       .attr('opacity', 0.9)
//       .style('cursor', 'pointer')
//       .style('filter', 'drop-shadow(0 2px 4px rgba(0,0,0,0.1))'); // Add subtle shadow

//     // Add blinking animation to edges
//     link.append('animate')
//       .attr('attributeName', 'opacity')
//       .attr('values', '0.3;1;0.3')
//       .attr('dur', '2s')
//       .attr('repeatCount', 'indefinite');

//     // Edge tooltip with closer positioning
//     const edgeTooltip = d3.select(svgRef.current.parentElement)
//       .append('div')
//       .attr('class', 'edge-tooltip')
//       .style('position', 'absolute')
//       .style('visibility', 'hidden')
//       .style('background', 'linear-gradient(135deg, #1f2937 0%, #374151 100%)')
//       .style('color', '#fff')
//       .style('border', '1px solid #4b5563')
//       .style('border-radius', '8px')
//       .style('padding', '10px 14px')
//       .style('pointer-events', 'none')
//       .style('z-index', '15')
//       .style('font-size', '13px')
//       .style('font-weight', '500')
//       .style('box-shadow', '0 8px 25px rgba(0, 0, 0, 0.2)')
//       .style('backdrop-filter', 'blur(8px)')
//       .style('min-width', '180px');

//     // Edge hover events with much closer positioning
//     link.on('mouseover', (event: MouseEvent, d: D3Link) => {
//       edgeTooltip.html(
//         `<div style="font-weight: 600; margin-bottom: 6px; color: #fbbf24;">🔄 ${d.action.toUpperCase()}</div>
//          <div style="margin-bottom: 3px;"><span style="color: #9ca3af;">From:</span> <span style="color: #e5e7eb;">${d.fromNetwork}</span></div>
//          <div style="margin-bottom: 3px;"><span style="color: #9ca3af;">To:</span> <span style="color: #e5e7eb;">${d.toNetwork}</span></div>
//          <div style="margin-bottom: 3px;"><span style="color: #9ca3af;">Energy:</span> <span style="color: #34d399;">${d.energyAmount} kWh</span></div>
//          <div style="margin-bottom: 3px;"><span style="color: #9ca3af;">Price:</span> <span style="color: #fbbf24;">₹${d.price}/kWh</span></div>
//          <div><span style="color: #9ca3af;">Status:</span> <span style="color: ${d.status === 'completed' ? '#22c55e' : '#f59e0b'};">${d.status}</span></div>`
//       )
//         .style('left', (event.pageX + 15) + 'px') // Very close to cursor, slight offset to avoid blocking
//         .style('top', (event.pageY - 20) + 'px') // Very close to cursor
//         .style('visibility', 'visible');
//     })
//       .on('mousemove', (event: MouseEvent) => {
//         edgeTooltip.style('left', (event.pageX + 15) + 'px')
//           .style('top', (event.pageY - 20) + 'px');
//       })
//       .on('mouseout', () => {
//         edgeTooltip.style('visibility', 'hidden');
//       });

//     // Draw nodes with enhanced visual appeal and different colors by type
//     const getNodeColor = (node: D3NetworkNode) => {
//       if (node.type === 'BAP') return node.status === 'SUBSCRIBED' ? '#3b82f6' : '#60a5fa'; // Blue
//       if (node.type === 'BPP') return node.status === 'SUBSCRIBED' ? '#22c55e' : '#4ade80'; // Green
//       if (node.type === 'BG') return node.status === 'SUBSCRIBED' ? '#f59e0b' : '#fbbf24'; // Orange
//       return '#6b7280'; // Gray fallback
//     };

//     const node = svg.append('g')
//       .selectAll('circle')
//       .data(nodes)
//       .enter().append('circle')
//       .attr('r', 32) // Slightly larger nodes
//       .attr('fill', (d: D3NetworkNode) => getNodeColor(d))
//       .attr('stroke', '#1e293b')
//       .attr('stroke-width', 3)
//       .style('filter', 'drop-shadow(0 4px 8px rgba(0,0,0,0.15))') // Enhanced shadow
//       .style('cursor', 'grab')
//       .call(d3.drag<SVGCircleElement, D3NetworkNode>()
//         .on('start', (event: d3.D3DragEvent<SVGCircleElement, D3NetworkNode, unknown>, d: D3NetworkNode) => {
//           if (!event.active) simulation.alphaTarget(0.3).restart();
//           d.fx = d.x;
//           d.fy = d.y;
//           d3.select(event.sourceEvent.target).style('cursor', 'grabbing');
//         })
//         .on('drag', (event: d3.D3DragEvent<SVGCircleElement, D3NetworkNode, unknown>, d: D3NetworkNode) => {
//           d.fx = event.x;
//           d.fy = event.y;
//         })
//         .on('end', (event: d3.D3DragEvent<SVGCircleElement, D3NetworkNode, unknown>, d: D3NetworkNode) => {
//           if (!event.active) simulation.alphaTarget(0);
//           d.fx = null;
//           d.fy = null;
//           d3.select(event.sourceEvent.target).style('cursor', 'grab');
//         })
//       );

//     // Enhanced tooltip with closer positioning and better design
//     const tooltip = d3.select(svgRef.current.parentElement)
//       .append('div')
//       .attr('class', 'beckn-tooltip')
//       .style('position', 'absolute')
//       .style('visibility', 'hidden')
//       .style('background', 'linear-gradient(135deg, #ffffff 0%, #f8fafc 100%)')
//       .style('border', '2px solid #e5e7eb')
//       .style('border-radius', '12px')
//       .style('padding', '16px')
//       .style('pointer-events', 'none')
//       .style('z-index', '10')
//       .style('box-shadow', '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)')
//       .style('font-size', '14px')
//       .style('max-width', '300px')
//       .style('backdrop-filter', 'blur(8px)')
//       .style('transform', 'translateZ(0)'); // Hardware acceleration

//     node.on('mouseover', (event: MouseEvent, d: D3NetworkNode) => {
//       tooltip.html(
//         `<div style="font-weight: 700; color: #1f2937; margin-bottom: 10px; font-size: 16px; display: flex; align-items: center;">
//            <div style="width: 12px; height: 12px; background: ${getNodeColor(d)}; border-radius: 50%; margin-right: 8px;"></div>
//            ${d.name}
//          </div>
//          <div style="margin-bottom: 6px;"><span style="color: #6b7280; font-weight: 500;">Type:</span> <span style="background: ${getNodeColor(d)}; color: white; padding: 2px 8px; border-radius: 6px; font-size: 12px; font-weight: 600;">${d.type}</span></div>
//          <div style="margin-bottom: 6px;"><span style="color: #6b7280; font-weight: 500;">Status:</span> <span style="color: ${d.status === 'SUBSCRIBED' ? '#22c55e' : '#f59e0b'}; font-weight: 600;">${d.status}</span></div>
//          <div style="margin-bottom: 6px;"><span style="color: #6b7280; font-weight: 500;">Providers:</span> <span style="color: #1f2937; font-weight: 600;">${d.provider_count}</span></div>
//          <div style="margin-bottom: 6px;"><span style="color: #6b7280; font-weight: 500;">Active Offers:</span> <span style="color: #1f2937; font-weight: 600;">${d.active_offers}</span></div>
//          <div style="margin-bottom: 8px;"><span style="color: #6b7280; font-weight: 500;">Coverage:</span> <span style="color: #1f2937; font-weight: 600;">${d.coverage_area.join(', ')}</span></div>
//          <div style="font-size: 11px; color: #9ca3af; margin-top: 8px; padding-top: 8px; border-top: 1px solid #e5e7eb; font-family: monospace;">${d.subscriber_id}</div>`
//       )
//         .style('left', (event.pageX + 20) + 'px') // Very close to cursor with small offset
//         .style('top', (event.pageY - 30) + 'px')  // Very close to cursor
//         .style('visibility', 'visible');
//     })
//       .on('mousemove', (event: MouseEvent) => {
//         tooltip.style('left', (event.pageX + 20) + 'px')
//           .style('top', (event.pageY - 30) + 'px');
//       })
//       .on('mouseout', () => {
//         tooltip.style('visibility', 'hidden');
//       });

//     // Enhanced node labels with better positioning
//     svg.append('g')
//       .selectAll('text')
//       .data(nodes)
//       .enter().append('text')
//       .attr('text-anchor', 'middle')
//       .attr('dy', 5)
//       .attr('font-size', 14) // Slightly larger font
//       .attr('font-weight', 700) // Bolder font
//       .attr('fill', '#ffffff') // White text for better contrast
//       .attr('stroke', '#1e293b') // Dark outline
//       .attr('stroke-width', 0.5)
//       .attr('paint-order', 'stroke fill') // Render stroke behind fill
//       .text((d: D3NetworkNode) => d.name.length > 10 ? d.name.slice(0, 10) + '…' : d.name);

//     // Add secondary labels below nodes
//     svg.append('g')
//       .selectAll('text.secondary')
//       .data(nodes)
//       .enter().append('text')
//       .attr('class', 'secondary')
//       .attr('text-anchor', 'middle')
//       .attr('dy', 50) // Closer to nodes
//       .attr('font-size', 11)
//       .attr('font-weight', 600)
//       .attr('fill', '#6b7280')
//       .text((d: D3NetworkNode) => d.type);

//     // Enhanced arrow marker for edges
//     svg.append('defs').append('marker')
//       .attr('id', 'arrow')
//       .attr('viewBox', '0 -5 10 10')
//       .attr('refX', 28) // Adjusted for larger nodes
//       .attr('refY', 0)
//       .attr('markerWidth', 8) // Larger arrow
//       .attr('markerHeight', 8)
//       .attr('orient', 'auto')
//       .append('path')
//       .attr('d', 'M0,-5L10,0L0,5')
//       .attr('fill', '#38bdf8')
//       .attr('stroke', '#1e293b')
//       .attr('stroke-width', 0.5);

//     simulation.on('tick', () => {
//       link
//         .attr('x1', d => (typeof d.source === 'object' && d.source.x !== undefined ? d.source.x : 0))
//         .attr('y1', d => (typeof d.source === 'object' && d.source.y !== undefined ? d.source.y : 0))
//         .attr('x2', d => (typeof d.target === 'object' && d.target.x !== undefined ? d.target.x : 0))
//         .attr('y2', d => (typeof d.target === 'object' && d.target.y !== undefined ? d.target.y : 0));
//       node
//         .attr('cx', (d: D3NetworkNode) => d.x ?? 0)
//         .attr('cy', (d: D3NetworkNode) => d.y ?? 0);
//       svg.selectAll('text')
//         .attr('x', (d: any) => d.x ?? 0)
//         .attr('y', (d: any) => (d.y ?? 0));
//       svg.selectAll('text.secondary')
//         .attr('x', (d: any) => d.x ?? 0)
//         .attr('y', (d: any) => (d.y ?? 0));
//     });

//     // Clean up tooltips on unmount
//     return () => {
//       tooltip.remove();
//       edgeTooltip.remove();
//     };
//   }, [participants, transactions]);

//   return (
//     <div style={{ position: 'relative', width: '100%', minHeight: 520 }}>
//       {/* Status indicator */}
//       <div style={{ 
//         position: 'absolute', 
//         top: 15, 
//         right: 15, 
//         background: participants && participants.length > 0 ? 
//           'linear-gradient(135deg, #22c55e 0%, #16a34a 100%)' : 
//           'linear-gradient(135deg, #f59e0b 0%, #d97706 100%)',
//         color: 'white',
//         padding: '8px 12px',
//         borderRadius: '8px',
//         fontSize: '12px',
//         fontWeight: 700,
//         zIndex: 20,
//         boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
//         border: '1px solid rgba(255,255,255,0.2)'
//       }}>
//         {participants && participants.length > 0 ? '🟢 Live Data' : '🔄 Demo Data'}
//       </div>
      
//       {/* Enhanced Legend */}
//       <div style={{
//         position: 'absolute',
//         top: 15,
//         left: 15,
//         background: 'linear-gradient(135deg, rgba(255, 255, 255, 0.98) 0%, rgba(248, 250, 252, 0.95) 100%)',
//         border: '2px solid #e5e7eb',
//         borderRadius: '12px',
//         padding: '16px',
//         fontSize: '13px',
//         zIndex: 20,
//         boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.1)',
//         backdropFilter: 'blur(8px)',
//         minWidth: '200px'
//       }}>
//         <div style={{ fontWeight: 700, marginBottom: '12px', color: '#1f2937', fontSize: '14px' }}>🌐 Network Types</div>
//         <div style={{ display: 'flex', alignItems: 'center', marginBottom: '6px' }}>
//           <div style={{ width: '14px', height: '14px', background: '#3b82f6', borderRadius: '50%', marginRight: '8px', border: '2px solid #1e40af' }}></div>
//           <span style={{ fontWeight: 600 }}>BAP (Buyer App)</span>
//         </div>
//         <div style={{ display: 'flex', alignItems: 'center', marginBottom: '6px' }}>
//           <div style={{ width: '14px', height: '14px', background: '#22c55e', borderRadius: '50%', marginRight: '8px', border: '2px solid #16a34a' }}></div>
//           <span style={{ fontWeight: 600 }}>BPP (Provider App)</span>
//         </div>
//         <div style={{ display: 'flex', alignItems: 'center', marginBottom: '12px' }}>
//           <div style={{ width: '14px', height: '14px', background: '#f59e0b', borderRadius: '50%', marginRight: '8px', border: '2px solid #d97706' }}></div>
//           <span style={{ fontWeight: 600 }}>BG (Gateway)</span>
//         </div>
//         <div style={{ fontWeight: 700, marginBottom: '8px', color: '#1f2937', fontSize: '14px' }}>⚡ Transactions</div>
//         <div style={{ display: 'flex', alignItems: 'center', marginBottom: '4px' }}>
//           <div style={{ width: '20px', height: '3px', background: '#f59e42', marginRight: '8px', borderRadius: '2px' }}></div>
//           <span style={{ fontWeight: 600 }}>Init/Outgoing</span>
//         </div>
//         <div style={{ display: 'flex', alignItems: 'center' }}>
//           <div style={{ width: '20px', height: '3px', background: '#38bdf8', marginRight: '8px', borderRadius: '2px' }}></div>
//           <span style={{ fontWeight: 600 }}>Other/Incoming</span>
//         </div>
//       </div>
      
//       <svg ref={svgRef} width={800} height={500} style={{ 
//         width: '100%', 
//         height: 500, 
//         background: 'linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%)', 
//         borderRadius: 16,
//         border: '2px solid #e5e7eb'
//       }} />
//     </div>
//   );
// };


import React, { useMemo, useEffect } from 'react';
import ReactFlow, {
  Background,
  Controls,
  MiniMap,
  useNodesState,
  useEdgesState,
  Edge,
  Node,
  MarkerType,
  BaseEdge,
  EdgeProps,
  getBezierPath
} from 'reactflow';
import 'reactflow/dist/style.css';

interface NetworkParticipant {
  name: string;
  type: string;
  status: string;
  provider_count: number;
  active_offers: number;
  coverage_area: string[];
  subscriber_id: string;
}

interface LiveTransaction {
  id: string;
  fromNetwork: string;
  toNetwork: string;
  status: string;
  action: string;
  energyAmount: number;
  price: number;
  timestamp: string;
}

interface BecknNetworkGraphProps {
  participants: NetworkParticipant[];
  transactions: LiveTransaction[];
}

const fallbackParticipants: NetworkParticipant[] = [
  {
    name: 'PowerShare Platform', type: 'BAP', status: 'SUBSCRIBED', provider_count: 15, active_offers: 42, coverage_area: ['Mumbai', 'Delhi', 'Bangalore'], subscriber_id: 'powershare.energy.platform'
  },
  {
    name: 'Green Energy Hub', type: 'BPP', status: 'SUBSCRIBED', provider_count: 8, active_offers: 23, coverage_area: ['Pune', 'Chennai'], subscriber_id: 'green.energy.hub'
  },
  {
    name: 'Solar Trade Network', type: 'BPP', status: 'SUBSCRIBED', provider_count: 12, active_offers: 31, coverage_area: ['Hyderabad', 'Kolkata'], subscriber_id: 'solar.trade.network'
  },
  {
    name: 'Wind Power Co', type: 'BPP', status: 'ACTIVE', provider_count: 6, active_offers: 18, coverage_area: ['Gujarat', 'Rajasthan'], subscriber_id: 'wind.power.co'
  },
  {
    name: 'Hydro Energy Ltd', type: 'BPP', status: 'SUBSCRIBED', provider_count: 4, active_offers: 12, coverage_area: ['Kerala', 'Karnataka'], subscriber_id: 'hydro.energy.ltd'
  },
  {
    name: 'Metro Energy BAP', type: 'BAP', status: 'SUBSCRIBED', provider_count: 20, active_offers: 55, coverage_area: ['NCR', 'Gurgaon'], subscriber_id: 'metro.energy.bap'
  },
  {
    name: 'Rural Power Hub', type: 'BG', status: 'ACTIVE', provider_count: 25, active_offers: 68, coverage_area: ['Bihar', 'UP', 'MP'], subscriber_id: 'rural.power.hub'
  },
  {
    name: 'Clean Energy Network', type: 'BPP', status: 'SUBSCRIBED', provider_count: 10, active_offers: 28, coverage_area: ['Tamil Nadu', 'Andhra Pradesh'], subscriber_id: 'clean.energy.network'
  },
  {
    name: 'Smart Grid Solutions', type: 'BAP', status: 'ACTIVE', provider_count: 18, active_offers: 45, coverage_area: ['Haryana', 'Punjab'], subscriber_id: 'smart.grid.solutions'
  },
  {
    name: 'Renewable Energy Corp', type: 'BPP', status: 'SUBSCRIBED', provider_count: 14, active_offers: 38, coverage_area: ['Odisha', 'Jharkhand'], subscriber_id: 'renewable.energy.corp'
  },
  {
    name: 'Energy Gateway', type: 'BG', status: 'SUBSCRIBED', provider_count: 30, active_offers: 82, coverage_area: ['West Bengal', 'Assam'], subscriber_id: 'energy.gateway'
  },
  {
    name: 'Solar City Network', type: 'BPP', status: 'ACTIVE', provider_count: 7, active_offers: 19, coverage_area: ['Goa', 'Maharashtra'], subscriber_id: 'solar.city.network'
  },
  {
    name: 'Power Trading Hub', type: 'BAP', status: 'SUBSCRIBED', provider_count: 22, active_offers: 61, coverage_area: ['Himachal Pradesh', 'Uttarakhand'], subscriber_id: 'power.trading.hub'
  },
];

const fallbackTransactions: LiveTransaction[] = [
  { id: 'tx_demo_1', fromNetwork: 'PowerShare Platform', toNetwork: 'Green Energy Hub', status: 'completed', action: 'init', energyAmount: 50, price: 4.25, timestamp: new Date().toISOString() },
  { id: 'tx_demo_2', fromNetwork: 'Solar Trade Network', toNetwork: 'PowerShare Platform', status: 'completed', action: 'confirm', energyAmount: 75, price: 3.80, timestamp: new Date().toISOString() },
  { id: 'tx_demo_3', fromNetwork: 'Wind Power Co', toNetwork: 'Metro Energy BAP', status: 'pending', action: 'init', energyAmount: 35, price: 5.10, timestamp: new Date().toISOString() },
  { id: 'tx_demo_4', fromNetwork: 'Clean Energy Network', toNetwork: 'Smart Grid Solutions', status: 'completed', action: 'select', energyAmount: 60, price: 3.95, timestamp: new Date().toISOString() },
  { id: 'tx_demo_5', fromNetwork: 'Energy Gateway', toNetwork: 'Renewable Energy Corp', status: 'pending', action: 'confirm', energyAmount: 90, price: 4.50, timestamp: new Date().toISOString() },
  { id: 'tx_demo_6', fromNetwork: 'Power Trading Hub', toNetwork: 'Solar City Network', status: 'completed', action: 'init', energyAmount: 25, price: 5.75, timestamp: new Date().toISOString() }
];

const getNodeColor = (type: string, status: string) => {
  if (type === 'BAP') return status === 'SUBSCRIBED' ? '#3b82f6' : '#60a5fa';
  if (type === 'BPP') return status === 'SUBSCRIBED' ? '#22c55e' : '#4ade80';
  if (type === 'BG') return status === 'SUBSCRIBED' ? '#f59e0b' : '#fbbf24';
  return '#6b7280';
};

const CustomEdge = ({ id, sourceX, sourceY, targetX, targetY, data }: EdgeProps) => {
  const [edgePath] = getBezierPath({ sourceX, sourceY, targetX, targetY });

  return (
    <>
      <BaseEdge id={id} path={edgePath} style={data?.style} />
      <path
        d={edgePath}
        fill="none"
        strokeOpacity="0"
        strokeWidth={15}
        onMouseEnter={(e) => {
          const tooltip = document.getElementById('global-tooltip');
          if (tooltip) {
            tooltip.innerHTML = `
              <div style="font-weight: bold; margin-bottom: 6px;">${data?.action?.toUpperCase()}</div>
              <div>From: ${data?.from}</div>
              <div>To: ${data?.to}</div>
              <div>Energy: ${data?.energyAmount} kWh</div>
              <div>Price: ₹${data?.price}/kWh</div>
              <div>Status: ${data?.status}</div>
            `;
            tooltip.style.display = 'block';
          }
        }}
        onMouseMove={(e) => {
          const tooltip = document.getElementById('global-tooltip');
          if (tooltip) {
            tooltip.style.left = `${e.pageX + 10}px`;
            tooltip.style.top = `${e.pageY - 10}px`;
          }
        }}
        onMouseLeave={() => {
          const tooltip = document.getElementById('global-tooltip');
          if (tooltip) tooltip.style.display = 'none';
        }}
      />
    </>
  );
};

const BecknNetworkGraph: React.FC<BecknNetworkGraphProps> = ({ participants, transactions }) => {
  useEffect(() => {
    if (!document.getElementById('global-tooltip')) {
      const tooltip = document.createElement('div');
      tooltip.id = 'global-tooltip';
      tooltip.className = 'tooltip';
      Object.assign(tooltip.style, {
        position: 'fixed', background: 'rgba(17,24,39,0.95)', color: 'white', padding: '10px 14px', borderRadius: '8px',
        fontSize: '13px', pointerEvents: 'none', zIndex: 1000, maxWidth: '280px', fontFamily: 'system-ui, sans-serif',
        backdropFilter: 'blur(6px)', boxShadow: '0 4px 10px rgba(0,0,0,0.3)', display: 'none'
      });
      document.body.appendChild(tooltip);
    }
  }, []);

  const usedParticipants = participants.length ? participants : fallbackParticipants;
  const usedTransactions = transactions.length ? transactions : fallbackTransactions;

  const nodes: Node[] = useMemo(() => {
    return usedParticipants.map((p, index) => ({
      id: p.name,
      position: {
        x: (index % 5) * 260,
        y: Math.floor(index / 5) * 180,
      },
      data: {
        label: (
          <div
            onMouseEnter={(e) => {
              const tooltip = document.getElementById('global-tooltip');
              if (tooltip) {
                tooltip.innerHTML = `
                  <div style="font-weight: bold; margin-bottom: 6px;">${p.name}</div>
                  <div>Type: ${p.type}</div>
                  <div>Status: ${p.status}</div>
                  <div>Providers: ${p.provider_count}</div>
                  <div>Offers: ${p.active_offers}</div>
                  <div>Coverage: ${p.coverage_area.join(', ')}</div>
                `;
                tooltip.style.display = 'block';
              }
            }}
            onMouseMove={(e) => {
              const tooltip = document.getElementById('global-tooltip');
              if (tooltip) {
                tooltip.style.left = `${e.pageX + 15}px`;
                tooltip.style.top = `${e.pageY - 20}px`;
              }
            }}
            onMouseLeave={() => {
              const tooltip = document.getElementById('global-tooltip');
              if (tooltip) tooltip.style.display = 'none';
            }}
            style={{
              background: getNodeColor(p.type, p.status),
              padding: '10px',
              borderRadius: '8px',
              color: 'white',
              fontWeight: 600,
              textAlign: 'center',
              boxShadow: '0 2px 6px rgba(0,0,0,0.2)',
            }}
          >
            {p.name}<br />
            <small>{p.type}</small>
          </div>
        ),
      },
      style: {
        border: 'none',
        background: 'transparent'
      }
    }));
  }, [usedParticipants]);

  const edges: Edge[] = useMemo(() => {
    return usedTransactions.map(tx => ({
      id: tx.id,
      source: tx.fromNetwork,
      target: tx.toNetwork,
      type: 'custom',
      data: {
        action: tx.action,
        from: tx.fromNetwork,
        to: tx.toNetwork,
        energyAmount: tx.energyAmount,
        price: tx.price,
        status: tx.status,
        style: {
          stroke: tx.action === 'init' ? '#f59e42' : '#38bdf8',
          strokeWidth: 2,
        }
      },
      markerEnd: {
        type: MarkerType.ArrowClosed,
        color: tx.action === 'init' ? '#f59e42' : '#38bdf8',
      },
      label: `${tx.energyAmount} kWh @ ₹${tx.price}`,
      labelStyle: {
        fill: '#374151',
        fontWeight: 600,
        fontSize: 12
      },
    }));
  }, [usedTransactions]);

  const [nodesState, , onNodesChange] = useNodesState(nodes);
  const [edgesState, , onEdgesChange] = useEdgesState(edges);

  return (
    <div style={{ width: '100%', height: '600px', borderRadius: 16, overflow: 'hidden' }}>
      <ReactFlow
        nodes={nodesState}
        edges={edgesState}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        edgeTypes={{ custom: CustomEdge }}
        fitView
      >
        <Background gap={20} />
        <MiniMap nodeColor={n => '#a1a1aa'} />
        <Controls />
      </ReactFlow>
    </div>
  );
};

export default BecknNetworkGraph;
