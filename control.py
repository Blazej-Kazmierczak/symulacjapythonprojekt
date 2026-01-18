# src/sewage_sim/control.py

def control_station(st, alarms, dt):
    ww = st.wet_well
    lvl = ww.level_m

    # --- DEFINICJA PROGÓW ---
    L_STOP = 0.8          # Stop całkowity (suchobieg)
    L_START_1 = 2.0       # Start pierwszej pompy
    L_START_2 = 3.0       # Start drugiej pompy (kryzys)
    L_CRITICAL_CLOSE = 4.0 # Zamknięcie zasuwy
    L_CRITICAL_OPEN = 3.8  # Otwarcie zasuwy (histereza)

   
    swap_limit = getattr(st, 'swap_limit', 60)
    if not hasattr(st, 'swap_timer'): st.swap_timer = 0
    st.swap_timer += dt
    if st.swap_timer >= swap_limit:
        st.last_single_idx = (st.last_single_idx + 1) % 2
        st.swap_timer = 0

  
    fails_count = sum(1 for p in st.pumps if p.state.failed)
    manual_close = getattr(st, 'manual_valve_closed', False)
    current_valve = getattr(st, 'inlet_valve_closed', False)

    if manual_close or fails_count >= 2 or lvl >= L_CRITICAL_CLOSE:
        st.inlet_valve_closed = True
        if lvl >= L_CRITICAL_CLOSE:
            alarms.set(f"{st.name}.CRIT", f"ALARM: Poziom {lvl:.2f}m! Zasuwa zamknięta.")
    elif current_valve and lvl > L_CRITICAL_OPEN:
        
        st.inlet_valve_closed = True
    else:
        st.inlet_valve_closed = False
        alarms.clear(f"{st.name}.CRIT")

   
    avail_indices = [i for i, p in enumerate(st.pumps) if not p.state.failed]
    
    
    for i, p in enumerate(st.pumps):
        if p.state.enabled and p.state.failed:
            p.state.enabled = False 
            backup = (i + 1) % 2
            if backup in avail_indices:
                st.pumps[backup].state.enabled = True
                alarms.set(f"{st.name}.BACKUP", f"Awaria pompy {chr(65+i)}! Przejęcie przez {chr(65+backup)}")
            else:
                alarms.set(f"{st.name}.FAIL", "KRYTYCZNE: Brak sprawnych pomp!")

    
    any_running = any(p.state.enabled for p in st.pumps)

   
    if lvl <= L_STOP:
        
        for p in st.pumps:
            p.state.enabled = False
        alarms.clear(f"{st.name}.BACKUP")

    elif lvl >= L_START_2:
       
        for i in avail_indices:
            st.pumps[i].state.enabled = True

    elif lvl >= L_START_1:
        
        if not any_running:
            target = st.last_single_idx
            if target in avail_indices:
                st.pumps[target].state.enabled = True
            elif avail_indices:
                
                st.pumps[avail_indices[0]].state.enabled = True
