# The 511 dashboard

This page documents the companion dashboard and holds the full card
YAML for every card shown in the README. Click any heading to expand
its YAML.

This dashboard was built on The 511's Wisconsin entities. It's dark-
themed and leans on a handful of custom HACS cards; each card's full YAML
is below — click to expand and copy just the pieces you want.

## Required HACS frontend cards

Install these in HACS, then restart Home Assistant:

| Card | HACS repository | Used for |
|------|-----------------|----------|
| [button-card](https://github.com/romychab/lovelace-button-card) | `romychab/lovelace-button-card` | Road conditions, message signs, travel times |
| [swipe-card](https://github.com/rospogrigio/lovelace-swipe-card) | `rospogrigio/lovelace-swipe-card` | Camera and sign carousels |
| [auto-entities](https://github.com/thomasloven/lovelace-auto-entities) | `thomasloven/lovelace-auto-entities` | Current-delays list |
| [mushroom](https://github.com/piitaya/lovelace-mushroom) | `piitaya/lovelace-mushroom` | Section titles |
| [bubble-card](https://github.com/Clooos/Bubble-Card) | `Clooos/Bubble-Card` | Message-sign pop-up |
| [card-mod](https://github.com/thomasloven/lovelace-card-mod) | `thomasloven/lovelace-card-mod` | Styling |

## Full dashboard

<video controls src="https://github.com/user-attachments/assets/373147c2-7203-4fab-a264-63d77372fad0"></video>

The whole dashboard on a desktop browser — road conditions and the
status header up top, cameras, message signs, travel times, incidents and
their map below.

## Road conditions

![Road conditions card](dashboard/screenshots/road_conditions.png)

A hazard-aware card. It scans every `sensor.the_511_*` road condition,
counts the roads that are affected, prints the worst surface status, and
glows the card border red/amber/green to match. Tapping a listed road
opens its more-info dialog.

<details>
<summary>Card YAML</summary>

```yaml
type: custom:button-card
show_name: false
show_state: false
show_icon: false
styles:
  card:
    - background-color: "#000000"
    - border-radius: 10px
    - border: |-
        [[[
          var worst = 'normal';
          var hazardous = ['wet', 'slush', 'ice', 'snow', 'hazardous', 'flooded', 'closed', 'delay'];
          
          Object.keys(states).forEach(id => {
            if (id.startsWith('sensor.the_511_')) {
              var surf = String(states[id].attributes.surface || states[id].state || '').toLowerCase();
              if (['ice', 'snow', 'hazardous', 'flooded', 'closed'].some(h => surf.includes(h))) {
                worst = 'hazardous';
              } else if (['wet', 'slush', 'delay'].some(h => surf.includes(h)) && worst !== 'hazardous') {
                worst = 'wet';
              }
            }
          });
          
          if (worst === 'normal') return '1px solid rgba(76, 175, 80, 0.4)';
          if (worst === 'wet') return '1px solid rgba(255, 193, 7, 0.5)';
          return '1px solid rgba(244, 67, 54, 0.6)';
        ]]]
    - box-shadow: |-
        [[[
          var worst = 'normal';
          
          Object.keys(states).forEach(id => {
            if (id.startsWith('sensor.the_511_')) {
              var surf = String(states[id].attributes.surface || states[id].state || '').toLowerCase();
              if (['ice', 'snow', 'hazardous', 'flooded', 'closed'].some(h => surf.includes(h))) {
                worst = 'hazardous';
              } else if (['wet', 'slush', 'delay'].some(h => surf.includes(h)) && worst !== 'hazardous') {
                worst = 'wet';
              }
            }
          });
          
          if (worst === 'normal') return '0 0 10px rgba(76, 175, 80, 0.1)';
          if (worst === 'wet') return '0 0 10px rgba(255, 193, 7, 0.15)';
          return '0 0 15px rgba(244, 67, 54, 0.2)';
        ]]]
    - padding: 12px 16px
  grid:
    - grid-template-areas: "\"header status\" \"main status\" \"footer footer\""
    - grid-template-columns: 1fr auto
    - grid-template-rows: auto auto auto
    - align-items: center
custom_fields:
  header: |-
    [[[
      return `<div style="color: #FFC107; font-size: 11px; font-weight: 800; letter-spacing: 1.5px; text-transform: uppercase; text-align: left;">ROAD CONDITIONS</div>`;
    ]]]
  main: |-
    [[[
      var affected = [];
      var hazardous = ['wet', 'slush', 'ice', 'snow', 'hazardous', 'flooded', 'closed', 'delay'];
      
      Object.keys(states).forEach(id => {
        if (id.startsWith('sensor.the_511_')) {
          var surf = String(states[id].attributes.surface || states[id].state || '').toLowerCase();
          if (hazardous.some(h => surf.includes(h))) {
            affected.push(states[id]);
          }
        }
      });
      
      var subtitle = affected.length > 0 ? `${affected.length} Roads Affected` : 'All Routes Clear';
      return `
        <div style="color: #FFFFFF; font-size: 15px; font-weight: 700; margin-top: 2px; text-align: left;">
          ${subtitle}
        </div>
      `;
    ]]]
  status: |-
    [[[
      var worstSurf = 'CLEAR';
      var color = '#4CAF50';
      
      Object.keys(states).forEach(id => {
        if (id.startsWith('sensor.the_511_')) {
          var surf = String(states[id].attributes.surface || states[id].state || '').toUpperCase();
          
          if (['ICE', 'SNOW', 'HAZARDOUS', 'FLOODED', 'CLOSED'].some(h => surf.includes(h))) {
            worstSurf = surf;
            color = '#F44336';
          } else if (['WET', 'SLUSH', 'DELAY'].some(h => surf.includes(h)) && worstSurf !== 'HAZARDOUS') {
            if (worstSurf === 'CLEAR') worstSurf = surf;
            color = '#FFC107';
          }
        }
      });

      return `
        <div style="display: flex; align-items: center; justify-content: flex-end;">
          <div style="border-left: 1px solid rgba(255, 255, 255, 0.12); padding-left: 16px; text-align: right;">
            <div style="color: #666666; font-size: 9px; font-weight: 700; letter-spacing: 1px; text-transform: uppercase; margin-bottom: 3px;">Status</div>
            <div style="color: ${color}; font-size: 18px; font-weight: 900; letter-spacing: 1px; line-height: 1;">${worstSurf}</div>
          </div>
        </div>
      `;
    ]]]
  footer: |-
    [[[
      var affectedNames = [];
      var hazardous = ['wet', 'slush', 'ice', 'snow', 'hazardous', 'flooded', 'closed', 'delay'];

      Object.keys(states).forEach(id => {
        if (id.startsWith('sensor.the_511_')) {
          var surf = String(states[id].attributes.surface || states[id].state || '').toLowerCase();
          if (hazardous.some(h => surf.includes(h))) {
            var name = states[id].attributes.friendly_name || id.replace('sensor.the_511_', '').replace(/_/g, ' ');
            affectedNames.push(`<strong style="color: #FFFFFF;">${name}:</strong> <span style="color: #FFC107;">${surf.toUpperCase()}</span>`);
          }
        }
      });

      if (affectedNames.length === 0) {
        return `
          <div style="margin-top: 10px; padding-top: 8px; border-top: 1px solid rgba(255, 255, 255, 0.08); font-size: 11px; color: #888888;">
            No active hazards reported across monitored corridors.
          </div>
        `;
      }

      return `
        <div style="margin-top: 10px; padding-top: 8px; border-top: 1px solid rgba(255, 255, 255, 0.08); font-size: 11px; color: #888888; display: flex; flex-direction: column; gap: 4px;">
          ${affectedNames.slice(0, 3).join('')}
        </div>
      `;
    ]]]
```

</details>

## Active incidents

![Active incidents card](dashboard/screenshots/active_incidents.png)

A markdown card that lists every active incident binary sensor
(`binary_sensor.the_511_*`), reformatting the names into a readable
"ROAD @ interchange" layout with dividers, or showing a green
"No Active Incidents" when the roads are clear.

<details>
<summary>Card YAML</summary>

```yaml
type: markdown
title: ⚠️ Active Incidents
content: >-
  {% set active = states.binary_sensor
     | selectattr('entity_id', 'search', '^binary_sensor\.the_511_')
     | selectattr('state', 'eq', 'on')
     | list %}

  {% if active %}

  <span class="active-count">{{ active | count }} Active Incident{{ '' if
  active|count == 1 else 's' }}</span>

  {% for inc in active %}

  <hr class="incident-divider">

  {% set text = inc.attributes.friendly_name
      | replace('The 511 ', '')
      | replace(' North', ' NB')
      | replace(' South', ' SB')
      | replace(' East', ' EB')
      | replace(' West', ' WB')
      | replace(' from ', ' @ ')
      | replace(' on ', '\n')
      | replace('. ', '.\n')
  %}

  {{ text }}

  {% endfor %}

  {% else %}

  <div class="no-incidents">🟢 No Active Incidents</div>

  {% endif %}
card_mod:
  style: |
    ha-card {
      background-color: #000000 !important;
      border-radius: 12px !important;
      padding: 18px 16px !important;
      border: none !important;
      box-shadow: none !important;
    }

    /* Card Title Styling */
    .card-header {
      color: #FFC107 !important;
      font-size: 20px !important;
      font-weight: 800 !important;
      padding: 0 0 12px 0 !important;
      letter-spacing: normal !important;
      text-align: left !important;
    }

    /* Markdown Body Styling */
    ha-markdown {
      color: #E0E0E0 !important;
      font-size: 14px !important;
      line-height: 1.5 !important;
    }

    /* Active Count Subtitle */
    .active-count {
      color: #FFC107;
      font-weight: 600;
      font-size: 14px;
      display: block;
      margin-bottom: 6px;
    }

    /* Matching Divider Lines */
    hr.incident-divider {
      border: none !important;
      border-top: 1px solid rgba(255, 255, 255, 0.08) !important;
      margin: 10px 0 !important;
    }

    /* "No Active Incidents" Text */
    .no-incidents {
      color: #E0E0E0;
      font-size: 14px;
      font-weight: 500;
    }
```

</details>

## Incidents map

![Incidents map](dashboard/screenshots/map.png)

A dark-themed `map` card showing the incident `geo_location` markers
the integration publishes, with an amber accent and a dark tile filter.

<details>
<summary>Card YAML</summary>

```yaml
type: map
title: Incidents — WI 511
default_zoom: 8
geo_location_sources:
  - the511
entities: []
theme_mode: dark
card_mod:
  style:
    .: |
      ha-card {
        background: #000000 !important;
        border-radius: 12px !important;
        overflow: hidden;
        border: 1px solid rgba(255, 193, 7, 0.25) !important;
        box-shadow: 0 0 12px rgba(0, 0, 0, 0.8) !important;
      }
      /* Style the card header title */
      .card-header {
        background: #000000 !important;
        color: #FFC107 !important;
        font-weight: 800 !important;
        font-size: 14px !important;
        letter-spacing: 1px !important;
        text-transform: uppercase !important;
        padding: 12px 16px !important;
        border-bottom: 1px solid rgba(255, 255, 255, 0.08) !important;
      }
      /* Custom dark tint overlay for the map tile layer */
      ha-map {
        filter: invert(90%) hue-rotate(180deg) brightness(95%) contrast(90%) !important;
      }
```

</details>

## Traffic cameras

<video controls src="https://github.com/user-attachments/assets/1bf3126e-b6d7-4f9a-af7e-ee8d0922c4fb"></video>

A swipeable gallery of the camera entities nearest your home, styled as
dark picture cards that auto-advance every 8 seconds.

<details>
<summary>Card YAML</summary>

```yaml
type: custom:swipe-card
parameters:
  spaceBetween: 10
  effect: slide
  grabCursor: true
  simulateTouch: true
  autoplay:
    delay: 8000
    disableOnInteraction: false
    pauseOnMouseEnter: true
    pagination: false
    clickable: true
card_mod:
  style: |
    :host {
      --swiper-theme-color: #FFC107 !important;
      --swiper-pagination-color: #FFC107 !important;
      --swiper-pagination-bullet-inactive-color: #ffffff !important;
      --swiper-pagination-bullet-inactive-opacity: 0.3 !important;
    }
cards:
  - type: picture-glance
    title: I-94 at WIS 73
    camera_image: camera.the_511_i_94_at_wis_73
    camera_view: auto
    entities: []
    card_mod:
      style: >
        ha-card {
          background: #000000 !important;
          border-radius: 12px !important;
          overflow: hidden;
          border: 1px solid rgba(255, 193, 7, 0.2);
          display: flex !important;
          flex-direction: column !important;
        }

        #container { position: relative !important; flex: 1 1 auto !important; }

        .box { position: relative !important; background: #000000 !important;
        z-index: 1; padding: 8px 12px !important; }

        .title { color: #FFC107 !important; font-weight: 800 !important;
        font-size: 14px !important; white-space: nowrap !important; overflow:
        hidden !important; text-overflow: ellipsis !important; }

        #image { pointer-events: none; }
  - type: picture-glance
    title: I-94 at WIS 89
    camera_image: camera.the_511_i_94_at_wis_89
    camera_view: auto
    entities: []
    card_mod:
      style: >
        ha-card {
          background: #000000 !important;
          border-radius: 12px !important;
          overflow: hidden;
          border: 1px solid rgba(255, 193, 7, 0.2);
          display: flex !important;
          flex-direction: column !important;
        }

        #container { position: relative !important; flex: 1 1 auto !important; }

        .box { position: relative !important; background: #000000 !important;
        z-index: 1; padding: 8px 12px !important; }

        .title { color: #FFC107 !important; font-weight: 800 !important;
        font-size: 14px !important; white-space: nowrap !important; overflow:
        hidden !important; text-overflow: ellipsis !important; }

        #image { pointer-events: none; }
  - type: picture-glance
    title: US 151 at County N
    camera_image: camera.the_511_us_151_at_county_n
    camera_view: auto
    entities: []
    card_mod:
      style: >
        ha-card {
          background: #000000 !important;
          border-radius: 12px !important;
          overflow: hidden;
          border: 1px solid rgba(255, 193, 7, 0.2);
          display: flex !important;
          flex-direction: column !important;
        }

        #container { position: relative !important; flex: 1 1 auto !important; }

        .box { position: relative !important; background: #000000 !important;
        z-index: 1; padding: 8px 12px !important; }

        .title { color: #FFC107 !important; font-weight: 800 !important;
        font-size: 14px !important; white-space: nowrap !important; overflow:
        hidden !important; text-overflow: ellipsis !important; }

        #image { pointer-events: none; }
  - type: picture-glance
    title: I-94 at County N
    camera_image: camera.the_511_i_94_at_county_n
    camera_view: auto
    entities: []
    card_mod:
      style: >
        ha-card {
          background: #000000 !important;
          border-radius: 12px !important;
          overflow: hidden;
          border: 1px solid rgba(255, 193, 7, 0.2);
          display: flex !important;
          flex-direction: column !important;
        }

        #container { position: relative !important; flex: 1 1 auto !important; }

        .box { position: relative !important; background: #000000 !important;
        z-index: 1; padding: 8px 12px !important; }

        .title { color: #FFC107 !important; font-weight: 800 !important;
        font-size: 14px !important; white-space: nowrap !important; overflow:
        hidden !important; text-overflow: ellipsis !important; }

        #image { pointer-events: none; }
  - type: picture-glance
    title: US 151 at WIS 19
    camera_image: camera.the_511_us_151_at_wis_19
    camera_view: auto
    entities: []
    card_mod:
      style: >
        ha-card {
          background: #000000 !important;
          border-radius: 12px !important;
          overflow: hidden;
          border: 1px solid rgba(255, 193, 7, 0.2);
          display: flex !important;
          flex-direction: column !important;
        }

        #container { position: relative !important; flex: 1 1 auto !important; }

        .box { position: relative !important; background: #000000 !important;
        z-index: 1; padding: 8px 12px !important; }

        .title { color: #FFC107 !important; font-weight: 800 !important;
        font-size: 14px !important; white-space: nowrap !important; overflow:
        hidden !important; text-overflow: ellipsis !important; }

        #image { pointer-events: none; }
  - type: picture-glance
    title: US 151 at Main St
    camera_image: camera.the_511_us_151_at_main_st
    camera_view: auto
    entities: []
    card_mod:
      style: >
        ha-card {
          background: #000000 !important;
          border-radius: 12px !important;
          overflow: hidden;
          border: 1px solid rgba(255, 193, 7, 0.2);
          display: flex !important;
          flex-direction: column !important;
        }

        #container { position: relative !important; flex: 1 1 auto !important; }

        .box { position: relative !important; background: #000000 !important;
        z-index: 1; padding: 8px 12px !important; }

        .title { color: #FFC107 !important; font-weight: 800 !important;
        font-size: 14px !important; white-space: nowrap !important; overflow:
        hidden !important; text-overflow: ellipsis !important; }

        #image { pointer-events: none; }
  - type: picture-glance
    title: US 151 at County C
    camera_image: camera.the_511_us_151_at_county_c
    camera_view: auto
    entities: []
    card_mod:
      style: >
        ha-card {
          background: #000000 !important;
          border-radius: 12px !important;
          overflow: hidden;
          border: 1px solid rgba(255, 193, 7, 0.2);
          display: flex !important;
          flex-direction: column !important;
        }

        #container { position: relative !important; flex: 1 1 auto !important; }

        .box { position: relative !important; background: #000000 !important;
        z-index: 1; padding: 8px 12px !important; }

        .title { color: #FFC107 !important; font-weight: 800 !important;
        font-size: 14px !important; white-space: nowrap !important; overflow:
        hidden !important; text-overflow: ellipsis !important; }

        #image { pointer-events: none; }
  - type: picture-glance
    title: I-94 at WIS 26
    camera_image: camera.the_511_i_94_at_wis_26
    camera_view: auto
    entities: []
    card_mod:
      style: >
        ha-card {
          background: #000000 !important;
          border-radius: 12px !important;
          overflow: hidden;
          border: 1px solid rgba(255, 193, 7, 0.2);
          display: flex !important;
          flex-direction: column !important;
        }

        #container { position: relative !important; flex: 1 1 auto !important; }

        .box { position: relative !important; background: #000000 !important;
        z-index: 1; padding: 8px 12px !important; }

        .title { color: #FFC107 !important; font-weight: 800 !important;
        font-size: 14px !important; white-space: nowrap !important; overflow:
        hidden !important; text-overflow: ellipsis !important; }

        #image { pointer-events: none; }
  - type: picture-glance
    title: I-94 at Gaston Rd
    camera_image: camera.the_511_i_94_at_gaston_rd
    camera_view: auto
    entities: []
    card_mod:
      style: >
        ha-card {
          background: #000000 !important;
          border-radius: 12px !important;
          overflow: hidden;
          border: 1px solid rgba(255, 193, 7, 0.2);
          display: flex !important;
          flex-direction: column !important;
        }

        #container { position: relative !important; flex: 1 1 auto !important; }

        .box { position: relative !important; background: #000000 !important;
        z-index: 1; padding: 8px 12px !important; }

        .title { color: #FFC107 !important; font-weight: 800 !important;
        font-size: 14px !important; white-space: nowrap !important; overflow:
        hidden !important; text-overflow: ellipsis !important; }

        #image { pointer-events: none; }
  - type: picture-glance
    title: US 151 at American Pkwy
    camera_image: camera.the_511_us_151_at_american_pkwy
    camera_view: auto
    entities: []
    card_mod:
      style: >
        ha-card {
          background: #000000 !important;
          border-radius: 12px !important;
          overflow: hidden;
          border: 1px solid rgba(255, 193, 7, 0.2);
          display: flex !important;
          flex-direction: column !important;
        }

        #container { position: relative !important; flex: 1 1 auto !important; }

        .box { position: relative !important; background: #000000 !important;
        z-index: 1; padding: 8px 12px !important; }

        .title { color: #FFC107 !important; font-weight: 800 !important;
        font-size: 14px !important; white-space: nowrap !important; overflow:
        hidden !important; text-overflow: ellipsis !important; }

        #image { pointer-events: none; }
  - type: picture-glance
    title: I-94 at Sprecher Rd
    camera_image: camera.the_511_i_94_at_sprecher_rd
    camera_view: auto
    entities: []
    card_mod:
      style: >
        ha-card {
          background: #000000 !important;
          border-radius: 12px !important;
          overflow: hidden;
          border: 1px solid rgba(255, 193, 7, 0.2);
          display: flex !important;
          flex-direction: column !important;
        }

        #container { position: relative !important; flex: 1 1 auto !important; }

        .box { position: relative !important; background: #000000 !important;
        z-index: 1; padding: 8px 12px !important; }

        .title { color: #FFC107 !important; font-weight: 800 !important;
        font-size: 14px !important; white-space: nowrap !important; overflow:
        hidden !important; text-overflow: ellipsis !important; }

        #image { pointer-events: none; }
  - type: picture-glance
    title: I-39/90/94 at US 151
    camera_image: camera.the_511_i_39_90_94_at_us_151
    camera_view: auto
    entities: []
    card_mod:
      style: >
        ha-card {
          background: #000000 !important;
          border-radius: 12px !important;
          overflow: hidden;
          border: 1px solid rgba(255, 193, 7, 0.2);
          display: flex !important;
          flex-direction: column !important;
        }

        #container { position: relative !important; flex: 1 1 auto !important; }

        .box { position: relative !important; background: #000000 !important;
        z-index: 1; padding: 8px 12px !important; }

        .title { color: #FFC107 !important; font-weight: 800 !important;
        font-size: 14px !important; white-space: nowrap !important; overflow:
        hidden !important; text-overflow: ellipsis !important; }

        #image { pointer-events: none; }
  - type: picture-glance
    title: I-39/90/94 at County T
    camera_image: camera.the_511_i_39_90_94_at_county_t
    camera_view: auto
    entities: []
    card_mod:
      style: >
        ha-card {
          background: #000000 !important;
          border-radius: 12px !important;
          overflow: hidden;
          border: 1px solid rgba(255, 193, 7, 0.2);
          display: flex !important;
          flex-direction: column !important;
        }

        #container { position: relative !important; flex: 1 1 auto !important; }

        .box { position: relative !important; background: #000000 !important;
        z-index: 1; padding: 8px 12px !important; }

        .title { color: #FFC107 !important; font-weight: 800 !important;
        font-size: 14px !important; white-space: nowrap !important; overflow:
        hidden !important; text-overflow: ellipsis !important; }

        #image { pointer-events: none; }
  - type: picture-glance
    title: I-39/90 at County BN
    camera_image: camera.the_511_i_39_90_at_county_bn
    camera_view: auto
    entities: []
    card_mod:
      style: >
        ha-card {
          background: #000000 !important;
          border-radius: 12px !important;
          overflow: hidden;
          border: 1px solid rgba(255, 193, 7, 0.2);
          display: flex !important;
          flex-direction: column !important;
        }

        #container { position: relative !important; flex: 1 1 auto !important; }

        .box { position: relative !important; background: #000000 !important;
        z-index: 1; padding: 8px 12px !important; }

        .title { color: #FFC107 !important; font-weight: 800 !important;
        font-size: 14px !important; white-space: nowrap !important; overflow:
        hidden !important; text-overflow: ellipsis !important; }

        #image { pointer-events: none; }
  - type: picture-glance
    title: I-39/90 at I-94
    camera_image: camera.the_511_i_39_90_at_i_94
    camera_view: auto
    entities: []
    card_mod:
      style: >
        ha-card {
          background: #000000 !important;
          border-radius: 12px !important;
          overflow: hidden;
          border: 1px solid rgba(255, 193, 7, 0.2);
          display: flex !important;
          flex-direction: column !important;
        }

        #container { position: relative !important; flex: 1 1 auto !important; }

        .box { position: relative !important; background: #000000 !important;
        z-index: 1; padding: 8px 12px !important; }

        .title { color: #FFC107 !important; font-weight: 800 !important;
        font-size: 14px !important; white-space: nowrap !important; overflow:
        hidden !important; text-overflow: ellipsis !important; }

        #image { pointer-events: none; }
  - type: picture-glance
    title: I-94 at County X
    camera_image: camera.the_511_i_94_at_county_x
    camera_view: auto
    entities: []
    card_mod:
      style: >
        ha-card {
          background: #000000 !important;
          border-radius: 12px !important;
          overflow: hidden;
          border: 1px solid rgba(255, 193, 7, 0.2);
          display: flex !important;
          flex-direction: column !important;
        }

        #container { position: relative !important; flex: 1 1 auto !important; }

        .box { position: relative !important; background: #000000 !important;
        z-index: 1; padding: 8px 12px !important; }

        .title { color: #FFC107 !important; font-weight: 800 !important;
        font-size: 14px !important; white-space: nowrap !important; overflow:
        hidden !important; text-overflow: ellipsis !important; }

        #image { pointer-events: none; }
  - type: picture-glance
    title: US 12/18 at County AB
    camera_image: camera.the_511_us_12_18_at_county_ab
    camera_view: auto
    entities: []
    card_mod:
      style: >
        ha-card {
          background: #000000 !important;
          border-radius: 12px !important;
          overflow: hidden;
          border: 1px solid rgba(255, 193, 7, 0.2);
          display: flex !important;
          flex-direction: column !important;
        }

        #container { position: relative !important; flex: 1 1 auto !important; }

        .box { position: relative !important; background: #000000 !important;
        z-index: 1; padding: 8px 12px !important; }

        .title { color: #FFC107 !important; font-weight: 800 !important;
        font-size: 14px !important; white-space: nowrap !important; overflow:
        hidden !important; text-overflow: ellipsis !important; }

        #image { pointer-events: none; }
  - type: picture-glance
    title: I-39/90 at County BB/Cottage Grove Rd
    camera_image: camera.the_511_i_39_90_at_county_bb_cottage_grove_rd
    camera_view: auto
    entities: []
    card_mod:
      style: >
        ha-card {
          background: #000000 !important;
          border-radius: 12px !important;
          overflow: hidden;
          border: 1px solid rgba(255, 193, 7, 0.2);
          display: flex !important;
          flex-direction: column !important;
        }

        #container { position: relative !important; flex: 1 1 auto !important; }

        .box { position: relative !important; background: #000000 !important;
        z-index: 1; padding: 8px 12px !important; }

        .title { color: #FFC107 !important; font-weight: 800 !important;
        font-size: 14px !important; white-space: nowrap !important; overflow:
        hidden !important; text-overflow: ellipsis !important; }

        #image { pointer-events: none; }
  - type: picture-glance
    title: I-39/90 at Buckeye Rd/County AB
    camera_image: camera.the_511_i_39_90_at_buckeye_rd_county_ab
    camera_view: auto
    entities: []
    card_mod:
      style: >
        ha-card {
          background: #000000 !important;
          border-radius: 12px !important;
          overflow: hidden;
          border: 1px solid rgba(255, 193, 7, 0.2);
          display: flex !important;
          flex-direction: column !important;
        }

        #container { position: relative !important; flex: 1 1 auto !important; }

        .box { position: relative !important; background: #000000 !important;
        z-index: 1; padding: 8px 12px !important; }

        .title { color: #FFC107 !important; font-weight: 800 !important;
        font-size: 14px !important; white-space: nowrap !important; overflow:
        hidden !important; text-overflow: ellipsis !important; }

        #image { pointer-events: none; }
  - type: picture-glance
    title: E Washington Ave at Continental Ln
    camera_image: camera.the_511_e_washington_ave_at_continental_ln
    camera_view: auto
    entities: []
    card_mod:
      style: >
        ha-card {
          background: #000000 !important;
          border-radius: 12px !important;
          overflow: hidden;
          border: 1px solid rgba(255, 193, 7, 0.2);
          display: flex !important;
          flex-direction: column !important;
        }

        #container { position: relative !important; flex: 1 1 auto !important; }

        .box { position: relative !important; background: #000000 !important;
        z-index: 1; padding: 8px 12px !important; }

        .title { color: #FFC107 !important; font-weight: 800 !important;
        font-size: 14px !important; white-space: nowrap !important; overflow:
        hidden !important; text-overflow: ellipsis !important; }

        #image { pointer-events: none; }
  - type: picture-glance
    title: US 51 at WIS 19
    camera_image: camera.the_511_us_51_at_wis_19
    camera_view: auto
    entities: []
    card_mod:
      style: >
        ha-card {
          background: #000000 !important;
          border-radius: 12px !important;
          overflow: hidden;
          border: 1px solid rgba(255, 193, 7, 0.2);
          display: flex !important;
          flex-direction: column !important;
        }

        #container { position: relative !important; flex: 1 1 auto !important; }

        .box { position: relative !important; background: #000000 !important;
        z-index: 1; padding: 8px 12px !important; }

        .title { color: #FFC107 !important; font-weight: 800 !important;
        font-size: 14px !important; white-space: nowrap !important; overflow:
        hidden !important; text-overflow: ellipsis !important; }

        #image { pointer-events: none; }
  - type: picture-glance
    title: I-39/90/94 at US 51
    camera_image: camera.the_511_i_39_90_94_at_us_51
    camera_view: auto
    entities: []
    card_mod:
      style: >
        ha-card {
          background: #000000 !important;
          border-radius: 12px !important;
          overflow: hidden;
          border: 1px solid rgba(255, 193, 7, 0.2);
          display: flex !important;
          flex-direction: column !important;
        }

        #container { position: relative !important; flex: 1 1 auto !important; }

        .box { position: relative !important; background: #000000 !important;
        z-index: 1; padding: 8px 12px !important; }

        .title { color: #FFC107 !important; font-weight: 800 !important;
        font-size: 14px !important; white-space: nowrap !important; overflow:
        hidden !important; text-overflow: ellipsis !important; }

        #image { pointer-events: none; }
  - type: picture-glance
    title: I-39/90 at County B
    camera_image: camera.the_511_i_39_90_at_county_b
    camera_view: auto
    entities: []
    card_mod:
      style: >
        ha-card {
          background: #000000 !important;
          border-radius: 12px !important;
          overflow: hidden;
          border: 1px solid rgba(255, 193, 7, 0.2);
          display: flex !important;
          flex-direction: column !important;
        }

        #container { position: relative !important; flex: 1 1 auto !important; }

        .box { position: relative !important; background: #000000 !important;
        z-index: 1; padding: 8px 12px !important; }

        .title { color: #FFC107 !important; font-weight: 800 !important;
        font-size: 14px !important; white-space: nowrap !important; overflow:
        hidden !important; text-overflow: ellipsis !important; }

        #image { pointer-events: none; }
  - type: picture-glance
    title: I-39/90 at County N
    camera_image: camera.the_511_i_39_90_at_county_n
    camera_view: auto
    entities: []
    card_mod:
      style: >
        ha-card {
          background: #000000 !important;
          border-radius: 12px !important;
          overflow: hidden;
          border: 1px solid rgba(255, 193, 7, 0.2);
          display: flex !important;
          flex-direction: column !important;
        }

        #container { position: relative !important; flex: 1 1 auto !important; }

        .box { position: relative !important; background: #000000 !important;
        z-index: 1; padding: 8px 12px !important; }

        .title { color: #FFC107 !important; font-weight: 800 !important;
        font-size: 14px !important; white-space: nowrap !important; overflow:
        hidden !important; text-overflow: ellipsis !important; }

        #image { pointer-events: none; }
  - type: picture-glance
    title: WIS 30 at Stoughton Rd
    camera_image: camera.the_511_wis_30_at_stoughton_rd
    camera_view: auto
    entities: []
    card_mod:
      style: >
        ha-card {
          background: #000000 !important;
          border-radius: 12px !important;
          overflow: hidden;
          border: 1px solid rgba(255, 193, 7, 0.2);
          display: flex !important;
          flex-direction: column !important;
        }

        #container { position: relative !important; flex: 1 1 auto !important; }

        .box { position: relative !important; background: #000000 !important;
        z-index: 1; padding: 8px 12px !important; }

        .title { color: #FFC107 !important; font-weight: 800 !important;
        font-size: 14px !important; white-space: nowrap !important; overflow:
        hidden !important; text-overflow: ellipsis !important; }

        #image { pointer-events: none; }
```

</details>

## Message signs

<video controls src="https://github.com/user-attachments/assets/0fdc84b4-3292-4be3-9c12-6fdf10af549e"></video>

Two parts. The first is a vertically-scrolling set of monospace
"MINUTES TO" sign cards, one per `sensor.the_511_sign_*` entity. The
second is a current-delays list that only appears while any sign reports
a delay (`delay` attribute > 0). Both use the sign's own attributes to
render the route, destination, minutes, and +delay.

<details>
<summary>Card YAML</summary>

```yaml
type: vertical-stack
cards:
  - type: custom:swipe-card
    parameters:
      direction: vertical
      height: 120
      autoplay:
        delay: 5000
        disableOnInteraction: false
      loop: true
      effect: slide
    card_mod:
      style: |
        .swiper-container {
          height: 120px !important;
        }
    cards:
      - type: custom:button-card
        entity: sensor.the_511_sign_325_i_94_eb_wis_26_to_us_18
        show_name: false
        show_state: false
        show_icon: false
        tap_action:
          action: navigate
          navigation_path: "#dmssign"
        styles:
          card:
            - background: "#0c0c0c"
            - border: 3px solid "#6a6a6a"
            - border-radius: 3px
            - height: 120px
            - padding: 0
            - overflow: hidden
            - position: relative
          custom_fields:
            header:
              - position: absolute
              - top: 8px
              - left: 0
              - width: 100%
              - text-align: center
              - color: "#ffb300"
              - font-size: 17px
              - font-family: monospace
              - letter-spacing: 4px
              - text-shadow: 0 0 2px rgba(255,176,0,0.75)
            route:
              - position: absolute
              - top: 42px
              - left: 18px
              - color: "#ffb300"
              - font-size: 24px
              - font-family: monospace
              - text-shadow: 0 0 2px rgba(255,176,0,0.75)
            destination:
              - position: absolute
              - top: 78px
              - left: 18px
              - color: "#ffb300"
              - font-size: 27px
              - font-family: monospace
              - text-shadow: 0 0 2px rgba(255,176,0,0.75)
            minutes:
              - position: absolute
              - top: 42px
              - right: 30px
              - color: "#ffb300"
              - font-size: 40px
              - font-family: monospace
              - font-weight: bold
              - line-height: 1
              - text-align: right
              - text-shadow: 0 0 2px rgba(255,176,0,0.75)
            delay:
              - position: absolute
              - top: 95px
              - right: 20px
              - width: 80px
              - text-align: center
              - color: "#ffb300"
              - font-size: 13px
              - font-family: monospace
              - font-weight: bold
              - text-shadow: 0 0 2px rgba(255,176,0,0.75)
        custom_fields:
          header: |
            [[[ return "MINUTES TO"; ]]]
          route: |
            [[[
              const road = entity.attributes.road || "";
              const dirMatch = entity.attributes.friendly_name ? entity.attributes.friendly_name.match(/\b(EB|WB|NB|SB)\b/i) : null;
              const dir = dirMatch ? dirMatch[1].toUpperCase() : "";
              return `${road} ${dir}`.trim();
            ]]]
          destination: |
            [[[
              const match = entity.attributes.friendly_name ? entity.attributes.friendly_name.match(/to (.*)/i) : null;
              return match ? match[1].toUpperCase() : "";
            ]]]
          minutes: |
            [[[ return Math.round(Number(entity.state)); ]]]
          delay: |
            [[[
              const delay = Number(entity.attributes.delay || 0);
              if (delay <= 0) return "";
              return `+${delay} MIN`;
            ]]]
      - type: custom:button-card
        entity: sensor.the_511_sign_325_i_94_eb_wis_26_to_wis_67
        show_name: false
        show_state: false
        show_icon: false
        tap_action: null
        action: navigate
        navigation_path: "#dmssign"
        styles:
          card:
            - background: "#0c0c0c"
            - border: 3px solid "#6a6a6a"
            - border-radius: 3px
            - height: 120px
            - padding: 0
            - overflow: hidden
            - position: relative
          custom_fields:
            header:
              - position: absolute
              - top: 8px
              - left: 0
              - width: 100%
              - text-align: center
              - color: "#ffb300"
              - font-size: 17px
              - font-family: monospace
              - letter-spacing: 4px
              - text-shadow: 0 0 2px rgba(255,176,0,0.75)
            route:
              - position: absolute
              - top: 42px
              - left: 18px
              - color: "#ffb300"
              - font-size: 24px
              - font-family: monospace
              - text-shadow: 0 0 2px rgba(255,176,0,0.75)
            destination:
              - position: absolute
              - top: 78px
              - left: 18px
              - color: "#ffb300"
              - font-size: 27px
              - font-family: monospace
              - text-shadow: 0 0 2px rgba(255,176,0,0.75)
            minutes:
              - position: absolute
              - top: 42px
              - right: 30px
              - color: "#ffb300"
              - font-size: 40px
              - font-family: monospace
              - font-weight: bold
              - line-height: 1
              - text-align: right
              - text-shadow: 0 0 2px rgba(255,176,0,0.75)
            delay:
              - position: absolute
              - top: 95px
              - right: 20px
              - width: 80px
              - text-align: center
              - color: "#ffb300"
              - font-size: 13px
              - font-family: monospace
              - font-weight: bold
              - text-shadow: 0 0 2px rgba(255,176,0,0.75)
        custom_fields:
          header: |
            [[[ return "MINUTES TO"; ]]]
          route: |
            [[[
              const road = entity.attributes.road || "";
              const dirMatch = entity.attributes.friendly_name ? entity.attributes.friendly_name.match(/\b(EB|WB|NB|SB)\b/i) : null;
              const dir = dirMatch ? dirMatch[1].toUpperCase() : "";
              return `${road} ${dir}`.trim();
            ]]]
          destination: |
            [[[
              const match = entity.attributes.friendly_name ? entity.attributes.friendly_name.match(/to (.*)/i) : null;
              return match ? match[1].toUpperCase() : "";
            ]]]
          minutes: |
            [[[ return Math.round(Number(entity.state)); ]]]
          delay: |
            [[[
              const delay = Number(entity.attributes.delay || 0);
              if (delay <= 0) return "";
              return `+${delay} MIN`;
            ]]]
      - type: custom:button-card
        entity: sensor.the_511_sign_311_i_94_eb_gaston_rd_to_wis_26
        show_name: false
        show_state: false
        show_icon: false
        tap_action:
          action: navigate
          navigation_path: "#dmssign"
        styles:
          card:
            - background: "#0c0c0c"
            - border: 3px solid "#6a6a6a"
            - border-radius: 3px
            - height: 120px
            - padding: 0
            - overflow: hidden
            - position: relative
          custom_fields:
            header:
              - position: absolute
              - top: 8px
              - left: 0
              - width: 100%
              - text-align: center
              - color: "#ffb300"
              - font-size: 17px
              - font-family: monospace
              - letter-spacing: 4px
              - text-shadow: 0 0 2px rgba(255,176,0,0.75)
            route:
              - position: absolute
              - top: 42px
              - left: 18px
              - color: "#ffb300"
              - font-size: 24px
              - font-family: monospace
              - text-shadow: 0 0 2px rgba(255,176,0,0.75)
            destination:
              - position: absolute
              - top: 78px
              - left: 18px
              - color: "#ffb300"
              - font-size: 27px
              - font-family: monospace
              - text-shadow: 0 0 2px rgba(255,176,0,0.75)
            minutes:
              - position: absolute
              - top: 42px
              - right: 30px
              - color: "#ffb300"
              - font-size: 40px
              - font-family: monospace
              - font-weight: bold
              - line-height: 1
              - text-align: right
              - text-shadow: 0 0 2px rgba(255,176,0,0.75)
            delay:
              - position: absolute
              - top: 95px
              - right: 20px
              - width: 80px
              - text-align: center
              - color: "#ffb300"
              - font-size: 13px
              - font-family: monospace
              - font-weight: bold
              - text-shadow: 0 0 2px rgba(255,176,0,0.75)
        custom_fields:
          header: |
            [[[ return "MINUTES TO"; ]]]
          route: |
            [[[
              const road = entity.attributes.road || "";
              const dirMatch = entity.attributes.friendly_name ? entity.attributes.friendly_name.match(/\b(EB|WB|NB|SB)\b/i) : null;
              const dir = dirMatch ? dirMatch[1].toUpperCase() : "";
              return `${road} ${dir}`.trim();
            ]]]
          destination: |
            [[[
              const match = entity.attributes.friendly_name ? entity.attributes.friendly_name.match(/to (.*)/i) : null;
              return match ? match[1].toUpperCase() : "";
            ]]]
          minutes: |
            [[[ return Math.round(Number(entity.state)); ]]]
          delay: |
            [[[
              const delay = Number(entity.attributes.delay || 0);
              if (delay <= 0) return "";
              return `+${delay} MIN`;
            ]]]
      - type: custom:button-card
        entity: sensor.the_511_sign_311_i_94_eb_gaston_rd_to_wis_89
        show_name: false
        show_state: false
        show_icon: false
        tap_action:
          action: navigate
          navigation_path: "#dmssign"
        styles:
          card:
            - background: "#0c0c0c"
            - border: 3px solid "#6a6a6a"
            - border-radius: 3px
            - height: 120px
            - padding: 0
            - overflow: hidden
            - position: relative
          custom_fields:
            header:
              - position: absolute
              - top: 8px
              - left: 0
              - width: 100%
              - text-align: center
              - color: "#ffb300"
              - font-size: 17px
              - font-family: monospace
              - letter-spacing: 4px
              - text-shadow: 0 0 2px rgba(255,176,0,0.75)
            route:
              - position: absolute
              - top: 42px
              - left: 18px
              - color: "#ffb300"
              - font-size: 24px
              - font-family: monospace
              - text-shadow: 0 0 2px rgba(255,176,0,0.75)
            destination:
              - position: absolute
              - top: 78px
              - left: 18px
              - color: "#ffb300"
              - font-size: 27px
              - font-family: monospace
              - text-shadow: 0 0 2px rgba(255,176,0,0.75)
            minutes:
              - position: absolute
              - top: 42px
              - right: 30px
              - color: "#ffb300"
              - font-size: 40px
              - font-family: monospace
              - font-weight: bold
              - line-height: 1
              - text-align: right
              - text-shadow: 0 0 2px rgba(255,176,0,0.75)
            delay:
              - position: absolute
              - top: 95px
              - right: 20px
              - width: 80px
              - text-align: center
              - color: "#ffb300"
              - font-size: 13px
              - font-family: monospace
              - font-weight: bold
              - text-shadow: 0 0 2px rgba(255,176,0,0.75)
        custom_fields:
          header: |
            [[[ return "MINUTES TO"; ]]]
          route: |
            [[[
              const road = entity.attributes.road || "";
              const dirMatch = entity.attributes.friendly_name ? entity.attributes.friendly_name.match(/\b(EB|WB|NB|SB)\b/i) : null;
              const dir = dirMatch ? dirMatch[1].toUpperCase() : "";
              return `${road} ${dir}`.trim();
            ]]]
          destination: |
            [[[
              const match = entity.attributes.friendly_name ? entity.attributes.friendly_name.match(/to (.*)/i) : null;
              return match ? match[1].toUpperCase() : "";
            ]]]
          minutes: |
            [[[ return Math.round(Number(entity.state)); ]]]
          delay: |
            [[[
              const delay = Number(entity.attributes.delay || 0);
              if (delay <= 0) return "";
              return `+${delay} MIN`;
            ]]]
      - type: custom:button-card
        entity: sensor.the_511_sign_312_i_94_wb_gaston_rd_to_john_nolen_dr
        show_name: false
        show_state: false
        show_icon: false
        tap_action:
          action: navigate
          navigation_path: "#dmssign"
        styles:
          card:
            - background: "#0c0c0c"
            - border: 3px solid "#6a6a6a"
            - border-radius: 3px
            - height: 120px
            - padding: 0
            - overflow: hidden
            - position: relative
          custom_fields:
            header:
              - position: absolute
              - top: 8px
              - left: 0
              - width: 100%
              - text-align: center
              - color: "#ffb300"
              - font-size: 17px
              - font-family: monospace
              - letter-spacing: 4px
              - text-shadow: 0 0 2px rgba(255,176,0,0.75)
            route:
              - position: absolute
              - top: 42px
              - left: 18px
              - color: "#ffb300"
              - font-size: 24px
              - font-family: monospace
              - text-shadow: 0 0 2px rgba(255,176,0,0.75)
            destination:
              - position: absolute
              - top: 78px
              - left: 18px
              - color: "#ffb300"
              - font-size: 27px
              - font-family: monospace
              - text-shadow: 0 0 2px rgba(255,176,0,0.75)
            minutes:
              - position: absolute
              - top: 42px
              - right: 30px
              - color: "#ffb300"
              - font-size: 40px
              - font-family: monospace
              - font-weight: bold
              - line-height: 1
              - text-align: right
              - text-shadow: 0 0 2px rgba(255,176,0,0.75)
            delay:
              - position: absolute
              - top: 95px
              - right: 20px
              - width: 80px
              - text-align: center
              - color: "#ffb300"
              - font-size: 13px
              - font-family: monospace
              - font-weight: bold
              - text-shadow: 0 0 2px rgba(255,176,0,0.75)
        custom_fields:
          header: |
            [[[ return "MINUTES TO"; ]]]
          route: |
            [[[
              const road = entity.attributes.road || "";
              const dirMatch = entity.attributes.friendly_name ? entity.attributes.friendly_name.match(/\b(EB|WB|NB|SB)\b/i) : null;
              const dir = dirMatch ? dirMatch[1].toUpperCase() : "";
              return `${road} ${dir}`.trim();
            ]]]
          destination: |
            [[[
              const match = entity.attributes.friendly_name ? entity.attributes.friendly_name.match(/to (.*)/i) : null;
              return match ? match[1].toUpperCase() : "";
            ]]]
          minutes: |
            [[[ return Math.round(Number(entity.state)); ]]]
          delay: |
            [[[
              const delay = Number(entity.attributes.delay || 0);
              if (delay <= 0) return "";
              return `+${delay} MIN`;
            ]]]
      - type: custom:button-card
        entity: sensor.the_511_sign_312_i_94_wb_gaston_rd_to_us_12_18
        show_name: false
        show_state: false
        show_icon: false
        tap_action:
          action: navigate
          navigation_path: "#dmssign"
        styles:
          card:
            - background: "#0c0c0c"
            - border: 3px solid "#6a6a6a"
            - border-radius: 3px
            - height: 120px
            - padding: 0
            - overflow: hidden
            - position: relative
          custom_fields:
            header:
              - position: absolute
              - top: 8px
              - left: 0
              - width: 100%
              - text-align: center
              - color: "#ffb300"
              - font-size: 17px
              - font-family: monospace
              - letter-spacing: 4px
              - text-shadow: 0 0 2px rgba(255,176,0,0.75)
            route:
              - position: absolute
              - top: 42px
              - left: 18px
              - color: "#ffb300"
              - font-size: 24px
              - font-family: monospace
              - text-shadow: 0 0 2px rgba(255,176,0,0.75)
            destination:
              - position: absolute
              - top: 78px
              - left: 18px
              - color: "#ffb300"
              - font-size: 27px
              - font-family: monospace
              - text-shadow: 0 0 2px rgba(255,176,0,0.75)
            minutes:
              - position: absolute
              - top: 42px
              - right: 30px
              - color: "#ffb300"
              - font-size: 40px
              - font-family: monospace
              - font-weight: bold
              - line-height: 1
              - text-align: right
              - text-shadow: 0 0 2px rgba(255,176,0,0.75)
            delay:
              - position: absolute
              - top: 95px
              - right: 20px
              - width: 80px
              - text-align: center
              - color: "#ffb300"
              - font-size: 13px
              - font-family: monospace
              - font-weight: bold
              - text-shadow: 0 0 2px rgba(255,176,0,0.75)
        custom_fields:
          header: |
            [[[ return "MINUTES TO"; ]]]
          route: |
            [[[
              const road = entity.attributes.road || "";
              const dirMatch = entity.attributes.friendly_name ? entity.attributes.friendly_name.match(/\b(EB|WB|NB|SB)\b/i) : null;
              const dir = dirMatch ? dirMatch[1].toUpperCase() : "";
              return `${road} ${dir}`.trim();
            ]]]
          destination: |
            [[[
              const match = entity.attributes.friendly_name ? entity.attributes.friendly_name.match(/to (.*)/i) : null;
              return match ? match[1].toUpperCase() : "";
            ]]]
          minutes: |
            [[[ return Math.round(Number(entity.state)); ]]]
          delay: |
            [[[
              const delay = Number(entity.attributes.delay || 0);
              if (delay <= 0) return "";
              return `+${delay} MIN`;
            ]]]
      - type: custom:button-card
        entity: sensor.the_511_sign_312_i_94_wb_gaston_rd_to_wis_19
        show_name: false
        show_state: false
        show_icon: false
        tap_action:
          action: navigate
          navigation_path: "#dmssign"
        styles:
          card:
            - background: "#0c0c0c"
            - border: 3px solid "#6a6a6a"
            - border-radius: 3px
            - height: 120px
            - padding: 0
            - overflow: hidden
            - position: relative
          custom_fields:
            header:
              - position: absolute
              - top: 8px
              - left: 0
              - width: 100%
              - text-align: center
              - color: "#ffb300"
              - font-size: 17px
              - font-family: monospace
              - letter-spacing: 4px
              - text-shadow: 0 0 2px rgba(255,176,0,0.75)
            route:
              - position: absolute
              - top: 42px
              - left: 18px
              - color: "#ffb300"
              - font-size: 24px
              - font-family: monospace
              - text-shadow: 0 0 2px rgba(255,176,0,0.75)
            destination:
              - position: absolute
              - top: 78px
              - left: 18px
              - color: "#ffb300"
              - font-size: 27px
              - font-family: monospace
              - text-shadow: 0 0 2px rgba(255,176,0,0.75)
            minutes:
              - position: absolute
              - top: 42px
              - right: 30px
              - color: "#ffb300"
              - font-size: 40px
              - font-family: monospace
              - font-weight: bold
              - line-height: 1
              - text-align: right
              - text-shadow: 0 0 2px rgba(255,176,0,0.75)
            delay:
              - position: absolute
              - top: 95px
              - right: 20px
              - width: 80px
              - text-align: center
              - color: "#ffb300"
              - font-size: 13px
              - font-family: monospace
              - font-weight: bold
              - text-shadow: 0 0 2px rgba(255,176,0,0.75)
        custom_fields:
          header: |
            [[[ return "MINUTES TO"; ]]]
          route: |
            [[[
              const road = entity.attributes.road || "";
              const dirMatch = entity.attributes.friendly_name ? entity.attributes.friendly_name.match(/\b(EB|WB|NB|SB)\b/i) : null;
              const dir = dirMatch ? dirMatch[1].toUpperCase() : "";
              return `${road} ${dir}`.trim();
            ]]]
          destination: |
            [[[
              const match = entity.attributes.friendly_name ? entity.attributes.friendly_name.match(/to (.*)/i) : null;
              return match ? match[1].toUpperCase() : "";
            ]]]
          minutes: |
            [[[ return Math.round(Number(entity.state)); ]]]
          delay: |
            [[[
              const delay = Number(entity.attributes.delay || 0);
              if (delay <= 0) return "";
              return `+${delay} MIN`;
            ]]]
      - type: custom:button-card
        entity: sensor.the_511_sign_305_i_39_90_94_sb_us_151_to_us_12_18
        show_name: false
        show_state: false
        show_icon: false
        tap_action:
          action: navigate
          navigation_path: "#dmssign"
        styles:
          card:
            - background: "#0c0c0c"
            - border: 3px solid "#6a6a6a"
            - border-radius: 3px
            - height: 120px
            - padding: 0
            - overflow: hidden
            - position: relative
          custom_fields:
            header:
              - position: absolute
              - top: 8px
              - left: 0
              - width: 100%
              - text-align: center
              - color: "#ffb300"
              - font-size: 17px
              - font-family: monospace
              - letter-spacing: 4px
              - text-shadow: 0 0 2px rgba(255,176,0,0.75)
            route:
              - position: absolute
              - top: 42px
              - left: 18px
              - color: "#ffb300"
              - font-size: 24px
              - font-family: monospace
              - text-shadow: 0 0 2px rgba(255,176,0,0.75)
            destination:
              - position: absolute
              - top: 78px
              - left: 18px
              - color: "#ffb300"
              - font-size: 27px
              - font-family: monospace
              - text-shadow: 0 0 2px rgba(255,176,0,0.75)
            minutes:
              - position: absolute
              - top: 42px
              - right: 30px
              - color: "#ffb300"
              - font-size: 40px
              - font-family: monospace
              - font-weight: bold
              - line-height: 1
              - text-align: right
              - text-shadow: 0 0 2px rgba(255,176,0,0.75)
            delay:
              - position: absolute
              - top: 95px
              - right: 20px
              - width: 80px
              - text-align: center
              - color: "#ffb300"
              - font-size: 13px
              - font-family: monospace
              - font-weight: bold
              - text-shadow: 0 0 2px rgba(255,176,0,0.75)
        custom_fields:
          header: |
            [[[ return "MINUTES TO"; ]]]
          route: |
            [[[
              const road = entity.attributes.road || "";
              const dirMatch = entity.attributes.friendly_name ? entity.attributes.friendly_name.match(/\b(EB|WB|NB|SB)\b/i) : null;
              const dir = dirMatch ? dirMatch[1].toUpperCase() : "";
              return `${road} ${dir}`.trim();
            ]]]
          destination: |
            [[[
              const match = entity.attributes.friendly_name ? entity.attributes.friendly_name.match(/to (.*)/i) : null;
              return match ? match[1].toUpperCase() : "";
            ]]]
          minutes: |
            [[[ return Math.round(Number(entity.state)); ]]]
          delay: |
            [[[
              const delay = Number(entity.attributes.delay || 0);
              if (delay <= 0) return "";
              return `+${delay} MIN`;
            ]]]
      - type: custom:button-card
        entity: sensor.the_511_sign_328_i_39_90_94_sb_lein_rd_to_i_94_at_county_n
        show_name: false
        show_state: false
        show_icon: false
        tap_action:
          action: navigate
          navigation_path: "#dmssign"
        styles:
          card:
            - background: "#0c0c0c"
            - border: 3px solid "#6a6a6a"
            - border-radius: 3px
            - height: 120px
            - padding: 0
            - overflow: hidden
            - position: relative
          custom_fields:
            header:
              - position: absolute
              - top: 8px
              - left: 0
              - width: 100%
              - text-align: center
              - color: "#ffb300"
              - font-size: 17px
              - font-family: monospace
              - letter-spacing: 4px
              - text-shadow: 0 0 2px rgba(255,176,0,0.75)
            route:
              - position: absolute
              - top: 42px
              - left: 18px
              - color: "#ffb300"
              - font-size: 24px
              - font-family: monospace
              - text-shadow: 0 0 2px rgba(255,176,0,0.75)
            destination:
              - position: absolute
              - top: 78px
              - left: 18px
              - color: "#ffb300"
              - font-size: 27px
              - font-family: monospace
              - text-shadow: 0 0 2px rgba(255,176,0,0.75)
            minutes:
              - position: absolute
              - top: 42px
              - right: 30px
              - color: "#ffb300"
              - font-size: 40px
              - font-family: monospace
              - font-weight: bold
              - line-height: 1
              - text-align: right
              - text-shadow: 0 0 2px rgba(255,176,0,0.75)
            delay:
              - position: absolute
              - top: 95px
              - right: 20px
              - width: 80px
              - text-align: center
              - color: "#ffb300"
              - font-size: 13px
              - font-family: monospace
              - font-weight: bold
              - text-shadow: 0 0 2px rgba(255,176,0,0.75)
        custom_fields:
          header: |
            [[[ return "MINUTES TO"; ]]]
          route: |
            [[[
              const road = entity.attributes.road || "";
              const dirMatch = entity.attributes.friendly_name ? entity.attributes.friendly_name.match(/\b(EB|WB|NB|SB)\b/i) : null;
              const dir = dirMatch ? dirMatch[1].toUpperCase() : "";
              return `${road} ${dir}`.trim();
            ]]]
          destination: |
            [[[
              const match = entity.attributes.friendly_name ? entity.attributes.friendly_name.match(/to (.*)/i) : null;
              return match ? match[1].toUpperCase() : "";
            ]]]
          minutes: |
            [[[ return Math.round(Number(entity.state)); ]]]
          delay: |
            [[[
              const delay = Number(entity.attributes.delay || 0);
              if (delay <= 0) return "";
              return `+${delay} MIN`;
            ]]]
      - type: custom:button-card
        entity: sensor.the_511_sign_328_i_39_90_94_sb_lein_rd_to_us_12_18
        show_name: false
        show_state: false
        show_icon: false
        tap_action:
          action: navigate
          navigation_path: "#dmssign"
        styles:
          card:
            - background: "#0c0c0c"
            - border: 3px solid "#6a6a6a"
            - border-radius: 3px
            - height: 120px
            - padding: 0
            - overflow: hidden
            - position: relative
          custom_fields:
            header:
              - position: absolute
              - top: 8px
              - left: 0
              - width: 100%
              - text-align: center
              - color: "#ffb300"
              - font-size: 17px
              - font-family: monospace
              - letter-spacing: 4px
              - text-shadow: 0 0 2px rgba(255,176,0,0.75)
            route:
              - position: absolute
              - top: 42px
              - left: 18px
              - color: "#ffb300"
              - font-size: 24px
              - font-family: monospace
              - text-shadow: 0 0 2px rgba(255,176,0,0.75)
            destination:
              - position: absolute
              - top: 78px
              - left: 18px
              - color: "#ffb300"
              - font-size: 27px
              - font-family: monospace
              - text-shadow: 0 0 2px rgba(255,176,0,0.75)
            minutes:
              - position: absolute
              - top: 42px
              - right: 30px
              - color: "#ffb300"
              - font-size: 40px
              - font-family: monospace
              - font-weight: bold
              - line-height: 1
              - text-align: right
              - text-shadow: 0 0 2px rgba(255,176,0,0.75)
            delay:
              - position: absolute
              - top: 95px
              - right: 20px
              - width: 80px
              - text-align: center
              - color: "#ffb300"
              - font-size: 13px
              - font-family: monospace
              - font-weight: bold
              - text-shadow: 0 0 2px rgba(255,176,0,0.75)
        custom_fields:
          header: |
            [[[ return "MINUTES TO"; ]]]
          route: |
            [[[
              const road = entity.attributes.road || "";
              const dirMatch = entity.attributes.friendly_name ? entity.attributes.friendly_name.match(/\b(EB|WB|NB|SB)\b/i) : null;
              const dir = dirMatch ? dirMatch[1].toUpperCase() : "";
              return `${road} ${dir}`.trim();
            ]]]
          destination: |
            [[[
              const match = entity.attributes.friendly_name ? entity.attributes.friendly_name.match(/to (.*)/i) : null;
              return match ? match[1].toUpperCase() : "";
            ]]]
          minutes: |
            [[[ return Math.round(Number(entity.state)); ]]]
          delay: |
            [[[
              const delay = Number(entity.attributes.delay || 0);
              if (delay <= 0) return "";
              return `+${delay} MIN`;
            ]]]
      - type: custom:button-card
        entity: sensor.the_511_sign_328_i_39_90_94_sb_lein_rd_to_us_12_18_at_park_st
        show_name: false
        show_state: false
        show_icon: false
        tap_action:
          action: navigate
          navigation_path: "#dmssign"
        styles:
          card:
            - background: "#0c0c0c"
            - border: 3px solid "#6a6a6a"
            - border-radius: 3px
            - height: 120px
            - padding: 0
            - overflow: hidden
            - position: relative
          custom_fields:
            header:
              - position: absolute
              - top: 8px
              - left: 0
              - width: 100%
              - text-align: center
              - color: "#ffb300"
              - font-size: 17px
              - font-family: monospace
              - letter-spacing: 4px
              - text-shadow: 0 0 2px rgba(255,176,0,0.75)
            route:
              - position: absolute
              - top: 42px
              - left: 18px
              - color: "#ffb300"
              - font-size: 24px
              - font-family: monospace
              - text-shadow: 0 0 2px rgba(255,176,0,0.75)
            destination:
              - position: absolute
              - top: 78px
              - left: 18px
              - color: "#ffb300"
              - font-size: 27px
              - font-family: monospace
              - text-shadow: 0 0 2px rgba(255,176,0,0.75)
            minutes:
              - position: absolute
              - top: 42px
              - right: 30px
              - color: "#ffb300"
              - font-size: 40px
              - font-family: monospace
              - font-weight: bold
              - line-height: 1
              - text-align: right
              - text-shadow: 0 0 2px rgba(255,176,0,0.75)
            delay:
              - position: absolute
              - top: 95px
              - right: 20px
              - width: 80px
              - text-align: center
              - color: "#ffb300"
              - font-size: 13px
              - font-family: monospace
              - font-weight: bold
              - text-shadow: 0 0 2px rgba(255,176,0,0.75)
        custom_fields:
          header: |
            [[[ return "MINUTES TO"; ]]]
          route: |
            [[[
              const road = entity.attributes.road || "";
              const dirMatch = entity.attributes.friendly_name ? entity.attributes.friendly_name.match(/\b(EB|WB|NB|SB)\b/i) : null;
              const dir = dirMatch ? dirMatch[1].toUpperCase() : "";
              return `${road} ${dir}`.trim();
            ]]]
          destination: |
            [[[
              const match = entity.attributes.friendly_name ? entity.attributes.friendly_name.match(/to (.*)/i) : null;
              return match ? match[1].toUpperCase() : "";
            ]]]
          minutes: |
            [[[ return Math.round(Number(entity.state)); ]]]
          delay: |
            [[[
              const delay = Number(entity.attributes.delay || 0);
              if (delay <= 0) return "";
              return `+${delay} MIN`;
            ]]]
      - type: custom:button-card
        entity: sensor.the_511_sign_339_i_39_90_nb_church_st_to_i_94
        show_name: false
        show_state: false
        show_icon: false
        tap_action:
          action: navigate
          navigation_path: "#dmssign"
        styles:
          card:
            - background: "#0c0c0c"
            - border: 3px solid "#6a6a6a"
            - border-radius: 3px
            - height: 120px
            - padding: 0
            - overflow: hidden
            - position: relative
          custom_fields:
            header:
              - position: absolute
              - top: 8px
              - left: 0
              - width: 100%
              - text-align: center
              - color: "#ffb300"
              - font-size: 17px
              - font-family: monospace
              - letter-spacing: 4px
              - text-shadow: 0 0 2px rgba(255,176,0,0.75)
            route:
              - position: absolute
              - top: 42px
              - left: 18px
              - color: "#ffb300"
              - font-size: 24px
              - font-family: monospace
              - text-shadow: 0 0 2px rgba(255,176,0,0.75)
            destination:
              - position: absolute
              - top: 78px
              - left: 18px
              - color: "#ffb300"
              - font-size: 27px
              - font-family: monospace
              - text-shadow: 0 0 2px rgba(255,176,0,0.75)
            minutes:
              - position: absolute
              - top: 42px
              - right: 30px
              - color: "#ffb300"
              - font-size: 40px
              - font-family: monospace
              - font-weight: bold
              - line-height: 1
              - text-align: right
              - text-shadow: 0 0 2px rgba(255,176,0,0.75)
            delay:
              - position: absolute
              - top: 95px
              - right: 20px
              - width: 80px
              - text-align: center
              - color: "#ffb300"
              - font-size: 13px
              - font-family: monospace
              - font-weight: bold
              - text-shadow: 0 0 2px rgba(255,176,0,0.75)
        custom_fields:
          header: |
            [[[ return "MINUTES TO"; ]]]
          route: |
            [[[
              const road = entity.attributes.road || "";
              const dirMatch = entity.attributes.friendly_name ? entity.attributes.friendly_name.match(/\b(EB|WB|NB|SB)\b/i) : null;
              const dir = dirMatch ? dirMatch[1].toUpperCase() : "";
              return `${road} ${dir}`.trim();
            ]]]
          destination: |
            [[[
              const match = entity.attributes.friendly_name ? entity.attributes.friendly_name.match(/to (.*)/i) : null;
              return match ? match[1].toUpperCase() : "";
            ]]]
          minutes: |
            [[[ return Math.round(Number(entity.state)); ]]]
          delay: |
            [[[
              const delay = Number(entity.attributes.delay || 0);
              if (delay <= 0) return "";
              return `+${delay} MIN`;
            ]]]
      - type: custom:button-card
        entity: sensor.the_511_sign_339_i_39_90_nb_church_st_to_us_12_18
        show_name: false
        show_state: false
        show_icon: false
        tap_action:
          action: navigate
          navigation_path: "#dmssign"
        styles:
          card:
            - background: "#0c0c0c"
            - border: 3px solid "#6a6a6a"
            - border-radius: 3px
            - height: 120px
            - padding: 0
            - overflow: hidden
            - position: relative
          custom_fields:
            header:
              - position: absolute
              - top: 8px
              - left: 0
              - width: 100%
              - text-align: center
              - color: "#ffb300"
              - font-size: 17px
              - font-family: monospace
              - letter-spacing: 4px
              - text-shadow: 0 0 2px rgba(255,176,0,0.75)
            route:
              - position: absolute
              - top: 42px
              - left: 18px
              - color: "#ffb300"
              - font-size: 24px
              - font-family: monospace
              - text-shadow: 0 0 2px rgba(255,176,0,0.75)
            destination:
              - position: absolute
              - top: 78px
              - left: 18px
              - color: "#ffb300"
              - font-size: 27px
              - font-family: monospace
              - text-shadow: 0 0 2px rgba(255,176,0,0.75)
            minutes:
              - position: absolute
              - top: 42px
              - right: 30px
              - color: "#ffb300"
              - font-size: 40px
              - font-family: monospace
              - font-weight: bold
              - line-height: 1
              - text-align: right
              - text-shadow: 0 0 2px rgba(255,176,0,0.75)
            delay:
              - position: absolute
              - top: 95px
              - right: 20px
              - width: 80px
              - text-align: center
              - color: "#ffb300"
              - font-size: 13px
              - font-family: monospace
              - font-weight: bold
              - text-shadow: 0 0 2px rgba(255,176,0,0.75)
        custom_fields:
          header: |
            [[[ return "MINUTES TO"; ]]]
          route: |
            [[[
              const road = entity.attributes.road || "";
              const dirMatch = entity.attributes.friendly_name ? entity.attributes.friendly_name.match(/\b(EB|WB|NB|SB)\b/i) : null;
              const dir = dirMatch ? dirMatch[1].toUpperCase() : "";
              return `${road} ${dir}`.trim();
            ]]]
          destination: |
            [[[
              const match = entity.attributes.friendly_name ? entity.attributes.friendly_name.match(/to (.*)/i) : null;
              return match ? match[1].toUpperCase() : "";
            ]]]
          minutes: |
            [[[ return Math.round(Number(entity.state)); ]]]
          delay: |
            [[[
              const delay = Number(entity.attributes.delay || 0);
              if (delay <= 0) return "";
              return `+${delay} MIN`;
            ]]]
      - type: custom:button-card
        entity: sensor.the_511_sign_326_i_94_wb_wis_26_to_i_39_90
        show_name: false
        show_state: false
        show_icon: false
        tap_action:
          action: navigate
          navigation_path: "#dmssign"
        styles:
          card:
            - background: "#0c0c0c"
            - border: 3px solid "#6a6a6a"
            - border-radius: 3px
            - height: 120px
            - padding: 0
            - overflow: hidden
            - position: relative
          custom_fields:
            header:
              - position: absolute
              - top: 8px
              - left: 0
              - width: 100%
              - text-align: center
              - color: "#ffb300"
              - font-size: 17px
              - font-family: monospace
              - letter-spacing: 4px
              - text-shadow: 0 0 2px rgba(255,176,0,0.75)
            route:
              - position: absolute
              - top: 42px
              - left: 18px
              - color: "#ffb300"
              - font-size: 24px
              - font-family: monospace
              - text-shadow: 0 0 2px rgba(255,176,0,0.75)
            destination:
              - position: absolute
              - top: 78px
              - left: 18px
              - color: "#ffb300"
              - font-size: 27px
              - font-family: monospace
              - text-shadow: 0 0 2px rgba(255,176,0,0.75)
            minutes:
              - position: absolute
              - top: 42px
              - right: 30px
              - color: "#ffb300"
              - font-size: 40px
              - font-family: monospace
              - font-weight: bold
              - line-height: 1
              - text-align: right
              - text-shadow: 0 0 2px rgba(255,176,0,0.75)
            delay:
              - position: absolute
              - top: 95px
              - right: 20px
              - width: 80px
              - text-align: center
              - color: "#ffb300"
              - font-size: 13px
              - font-family: monospace
              - font-weight: bold
              - text-shadow: 0 0 2px rgba(255,176,0,0.75)
        custom_fields:
          header: |
            [[[ return "MINUTES TO"; ]]]
          route: |
            [[[
              const road = entity.attributes.road || "";
              const dirMatch = entity.attributes.friendly_name ? entity.attributes.friendly_name.match(/\b(EB|WB|NB|SB)\b/i) : null;
              const dir = dirMatch ? dirMatch[1].toUpperCase() : "";
              return `${road} ${dir}`.trim();
            ]]]
          destination: |
            [[[
              const match = entity.attributes.friendly_name ? entity.attributes.friendly_name.match(/to (.*)/i) : null;
              return match ? match[1].toUpperCase() : "";
            ]]]
          minutes: |
            [[[ return Math.round(Number(entity.state)); ]]]
          delay: |
            [[[
              const delay = Number(entity.attributes.delay || 0);
              if (delay <= 0) return "";
              return `+${delay} MIN`;
            ]]]
      - type: custom:button-card
        entity: sensor.the_511_sign_326_i_94_wb_wis_26_to_wis_73
        show_name: false
        show_state: false
        show_icon: false
        tap_action:
          action: navigate
          navigation_path: "#dmssign"
        styles:
          card:
            - background: "#0c0c0c"
            - border: 3px solid "#6a6a6a"
            - border-radius: 3px
            - height: 120px
            - padding: 0
            - overflow: hidden
            - position: relative
          custom_fields:
            header:
              - position: absolute
              - top: 8px
              - left: 0
              - width: 100%
              - text-align: center
              - color: "#ffb300"
              - font-size: 17px
              - font-family: monospace
              - letter-spacing: 4px
              - text-shadow: 0 0 2px rgba(255,176,0,0.75)
            route:
              - position: absolute
              - top: 42px
              - left: 18px
              - color: "#ffb300"
              - font-size: 24px
              - font-family: monospace
              - text-shadow: 0 0 2px rgba(255,176,0,0.75)
            destination:
              - position: absolute
              - top: 78px
              - left: 18px
              - color: "#ffb300"
              - font-size: 27px
              - font-family: monospace
              - text-shadow: 0 0 2px rgba(255,176,0,0.75)
            minutes:
              - position: absolute
              - top: 42px
              - right: 30px
              - color: "#ffb300"
              - font-size: 40px
              - font-family: monospace
              - font-weight: bold
              - line-height: 1
              - text-align: right
              - text-shadow: 0 0 2px rgba(255,176,0,0.75)
            delay:
              - position: absolute
              - top: 95px
              - right: 20px
              - width: 80px
              - text-align: center
              - color: "#ffb300"
              - font-size: 13px
              - font-family: monospace
              - font-weight: bold
              - text-shadow: 0 0 2px rgba(255,176,0,0.75)
        custom_fields:
          header: |
            [[[ return "MINUTES TO"; ]]]
          route: |
            [[[
              const road = entity.attributes.road || "";
              const dirMatch = entity.attributes.friendly_name ? entity.attributes.friendly_name.match(/\b(EB|WB|NB|SB)\b/i) : null;
              const dir = dirMatch ? dirMatch[1].toUpperCase() : "";
              return `${road} ${dir}`.trim();
            ]]]
          destination: |
            [[[
              const match = entity.attributes.friendly_name ? entity.attributes.friendly_name.match(/to (.*)/i) : null;
              return match ? match[1].toUpperCase() : "";
            ]]]
          minutes: |
            [[[ return Math.round(Number(entity.state)); ]]]
          delay: |
            [[[
              const delay = Number(entity.attributes.delay || 0);
              if (delay <= 0) return "";
              return `+${delay} MIN`;
            ]]]
      - type: custom:button-card
        entity: sensor.the_511_sign_344_i_39_90_sb_cottage_grove_rd_to_wis_73
        show_name: false
        show_state: false
        show_icon: false
        tap_action:
          action: navigate
          navigation_path: "#dmssign"
        styles:
          card:
            - background: "#0c0c0c"
            - border: 3px solid "#6a6a6a"
            - border-radius: 3px
            - height: 120px
            - padding: 0
            - overflow: hidden
            - position: relative
          custom_fields:
            header:
              - position: absolute
              - top: 8px
              - left: 0
              - width: 100%
              - text-align: center
              - color: "#ffb300"
              - font-size: 17px
              - font-family: monospace
              - letter-spacing: 4px
              - text-shadow: 0 0 2px rgba(255,176,0,0.75)
            route:
              - position: absolute
              - top: 42px
              - left: 18px
              - color: "#ffb300"
              - font-size: 24px
              - font-family: monospace
              - text-shadow: 0 0 2px rgba(255,176,0,0.75)
            destination:
              - position: absolute
              - top: 78px
              - left: 18px
              - color: "#ffb300"
              - font-size: 27px
              - font-family: monospace
              - text-shadow: 0 0 2px rgba(255,176,0,0.75)
            minutes:
              - position: absolute
              - top: 42px
              - right: 30px
              - color: "#ffb300"
              - font-size: 40px
              - font-family: monospace
              - font-weight: bold
              - line-height: 1
              - text-align: right
              - text-shadow: 0 0 2px rgba(255,176,0,0.75)
            delay:
              - position: absolute
              - top: 95px
              - right: 20px
              - width: 80px
              - text-align: center
              - color: "#ffb300"
              - font-size: 13px
              - font-family: monospace
              - font-weight: bold
              - text-shadow: 0 0 2px rgba(255,176,0,0.75)
        custom_fields:
          header: |
            [[[ return "MINUTES TO"; ]]]
          route: |
            [[[
              const road = entity.attributes.road || "";
              const dirMatch = entity.attributes.friendly_name ? entity.attributes.friendly_name.match(/\b(EB|WB|NB|SB)\b/i) : null;
              const dir = dirMatch ? dirMatch[1].toUpperCase() : "";
              return `${road} ${dir}`.trim();
            ]]]
          destination: |
            [[[
              const match = entity.attributes.friendly_name ? entity.attributes.friendly_name.match(/to (.*)/i) : null;
              return match ? match[1].toUpperCase() : "";
            ]]]
          minutes: |
            [[[ return Math.round(Number(entity.state)); ]]]
          delay: |
            [[[
              const delay = Number(entity.attributes.delay || 0);
              if (delay <= 0) return "";
              return `+${delay} MIN`;
            ]]]
      - type: custom:button-card
        entity: sensor.the_511_sign_343_i_39_90_nb_cottage_grove_rd_to_us_151
        show_name: false
        show_state: false
        show_icon: false
        tap_action:
          action: navigate
          navigation_path: "#dmssign"
        styles:
          card:
            - background: "#0c0c0c"
            - border: 3px solid "#6a6a6a"
            - border-radius: 3px
            - height: 120px
            - padding: 0
            - overflow: hidden
            - position: relative
          custom_fields:
            header:
              - position: absolute
              - top: 8px
              - left: 0
              - width: 100%
              - text-align: center
              - color: "#ffb300"
              - font-size: 17px
              - font-family: monospace
              - letter-spacing: 4px
              - text-shadow: 0 0 2px rgba(255,176,0,0.75)
            route:
              - position: absolute
              - top: 42px
              - left: 18px
              - color: "#ffb300"
              - font-size: 24px
              - font-family: monospace
              - text-shadow: 0 0 2px rgba(255,176,0,0.75)
            destination:
              - position: absolute
              - top: 78px
              - left: 18px
              - color: "#ffb300"
              - font-size: 27px
              - font-family: monospace
              - text-shadow: 0 0 2px rgba(255,176,0,0.75)
            minutes:
              - position: absolute
              - top: 42px
              - right: 30px
              - color: "#ffb300"
              - font-size: 40px
              - font-family: monospace
              - font-weight: bold
              - line-height: 1
              - text-align: right
              - text-shadow: 0 0 2px rgba(255,176,0,0.75)
            delay:
              - position: absolute
              - top: 95px
              - right: 20px
              - width: 80px
              - text-align: center
              - color: "#ffb300"
              - font-size: 13px
              - font-family: monospace
              - font-weight: bold
              - text-shadow: 0 0 2px rgba(255,176,0,0.75)
        custom_fields:
          header: |
            [[[ return "MINUTES TO"; ]]]
          route: |
            [[[
              const road = entity.attributes.road || "";
              const dirMatch = entity.attributes.friendly_name ? entity.attributes.friendly_name.match(/\b(EB|WB|NB|SB)\b/i) : null;
              const dir = dirMatch ? dirMatch[1].toUpperCase() : "";
              return `${road} ${dir}`.trim();
            ]]]
          destination: |
            [[[
              const match = entity.attributes.friendly_name ? entity.attributes.friendly_name.match(/to (.*)/i) : null;
              return match ? match[1].toUpperCase() : "";
            ]]]
          minutes: |
            [[[ return Math.round(Number(entity.state)); ]]]
          delay: |
            [[[
              const delay = Number(entity.attributes.delay || 0);
              if (delay <= 0) return "";
              return `+${delay} MIN`;
            ]]]
  - type: custom:auto-entities
    card:
      type: custom:mushroom-title-card
      subtitle: ⚠️ CURRENT DELAYS
      card_mod:
        style: |
          ha-card {
            background: none !important;
            border: none !important;
            box-shadow: none !important;
          }

          .subtitle {
            color: #silver !important; /* Amber */
            font-weight: 600;
          }
    card_param: card
    filter:
      template: |-
        {% set delayed = states.sensor
          | selectattr('entity_id', 'search', '^sensor\.the_511_sign_')
          | selectattr('attributes.delay', 'defined')
          | selectattr('attributes.delay', 'gt', 0)
          | list %}
        {% if delayed | length > 0 %}
          true
        {% endif %}
    filter_empty: true
  - type: custom:auto-entities
    card:
      type: vertical-stack
    card_param: cards
    header: >
      <div style="font-family: monospace; font-size: 14px; font-weight: bold;
      color: #ffb300; text-transform: uppercase; letter-spacing: 2px; padding:
      12px 4px 4px 4px; text-shadow: 0 0 2px rgba(255,176,0,0.75);">
        ⚠ CURRENT DELAYS
      </div>
    filter:
      include:
        - domain: sensor
          entity_id: sensor.the_511_sign_*
          attributes:
            delay: "> 0"
          options:
            type: custom:button-card
            show_name: false
            show_state: false
            show_icon: false
            tap_action:
              action: navigate
              navigation_path: "#dmssign"
            styles:
              card:
                - background: "#0c0c0c"
                - border: 3px solid "#6a6a6a"
                - border-radius: 3px
                - height: 120px
                - padding: 0
                - overflow: hidden
                - position: relative
              custom_fields:
                header:
                  - position: absolute
                  - top: 8px
                  - left: 0
                  - width: 100%
                  - text-align: center
                  - color: "#ffb300"
                  - font-size: 17px
                  - font-family: monospace
                  - letter-spacing: 4px
                  - text-shadow: 0 0 2px rgba(255,176,0,0.75)
                route:
                  - position: absolute
                  - top: 42px
                  - left: 18px
                  - color: "#ffb300"
                  - font-size: 24px
                  - font-family: monospace
                  - text-shadow: 0 0 2px rgba(255,176,0,0.75)
                destination:
                  - position: absolute
                  - top: 78px
                  - left: 18px
                  - color: "#ffb300"
                  - font-size: 27px
                  - font-family: monospace
                  - text-shadow: 0 0 2px rgba(255,176,0,0.75)
                minutes:
                  - position: absolute
                  - top: 42px
                  - right: 30px
                  - color: "#ffb300"
                  - font-size: 40px
                  - font-family: monospace
                  - font-weight: bold
                  - line-height: 1
                  - text-align: right
                  - text-shadow: 0 0 2px rgba(255,176,0,0.75)
                delay:
                  - position: absolute
                  - top: 95px
                  - right: 20px
                  - width: 80px
                  - text-align: center
                  - color: "#ffb300"
                  - font-size: 13px
                  - font-family: monospace
                  - font-weight: bold
                  - text-shadow: 0 0 2px rgba(255,176,0,0.75)
            custom_fields:
              header: |
                [[[ return "MINUTES TO"; ]]]
              route: |
                [[[
                  const road = entity.attributes.road || "";
                  const dirMatch = entity.attributes.friendly_name ? entity.attributes.friendly_name.match(/\b(EB|WB|NB|SB)\b/i) : null;
                  const dir = dirMatch ? dirMatch[1].toUpperCase() : "";
                  return `${road} ${dir}`.trim();
                ]]]
              destination: |
                [[[
                  const match = entity.attributes.friendly_name ? entity.attributes.friendly_name.match(/to (.*)/i) : null;
                  return match ? match[1].toUpperCase() : "";
                ]]]
              minutes: |
                [[[ return Math.round(Number(entity.state)); ]]]
              delay: |
                [[[
                  const delay = Number(entity.attributes.delay || 0);
                  if (delay <= 0) return "";
                  return `+${delay} MIN`;
                ]]]
    filter_empty: true
```

</details>

## Message sign pop-up

The bubble-card pop-up the sign cards open when tapped (`hash:
"#dmssign"`). It's optional — add it once anywhere in the dashboard and
the sign cards' tap actions will slide it up with every sign, each
opening its own more-info on tap.

<details>
<summary>Card YAML</summary>

```yaml
type: custom:bubble-card
card_type: pop-up
hash: "#dmssign"
cards:
  - type: vertical-stack
    cards:
      - type: custom:button-card
        entity: sensor.the_511_sign_325_i_94_eb_wis_26_to_us_18
        show_name: false
        show_state: false
        show_icon: false
        tap_action:
          action: more-info
        styles:
          card:
            - background: "#0c0c0c"
            - border: 3px solid "#6a6a6a"
            - border-radius: 3px
            - height: 120px
            - padding: 0
            - overflow: hidden
            - position: relative
          custom_fields:
            header:
              - position: absolute
              - top: 8px
              - left: 0
              - width: 100%
              - text-align: center
              - color: "#ffb300"
              - font-size: 17px
              - font-family: monospace
              - letter-spacing: 4px
              - text-shadow: 0 0 2px rgba(255,176,0,0.75)
            route:
              - position: absolute
              - top: 42px
              - left: 18px
              - color: "#ffb300"
              - font-size: 24px
              - font-family: monospace
              - text-shadow: 0 0 2px rgba(255,176,0,0.75)
            destination:
              - position: absolute
              - top: 78px
              - left: 18px
              - color: "#ffb300"
              - font-size: 27px
              - font-family: monospace
              - text-shadow: 0 0 2px rgba(255,176,0,0.75)
            minutes:
              - position: absolute
              - top: 42px
              - right: 30px
              - color: "#ffb300"
              - font-size: 40px
              - font-family: monospace
              - font-weight: bold
              - line-height: 1
              - text-align: right
              - text-shadow: 0 0 2px rgba(255,176,0,0.75)
            delay:
              - position: absolute
              - top: 95px
              - right: 20px
              - width: 80px
              - text-align: center
              - color: "#ffb300"
              - font-size: 13px
              - font-family: monospace
              - font-weight: bold
              - text-shadow: 0 0 2px rgba(255,176,0,0.75)
        custom_fields:
          header: |
            [[[ return "MINUTES TO"; ]]]
          route: |
            [[[
              const road = entity.attributes.road || "";
              const dirMatch = entity.attributes.friendly_name ? entity.attributes.friendly_name.match(/\b(EB|WB|NB|SB)\b/i) : null;
              const dir = dirMatch ? dirMatch[1].toUpperCase() : "";
              return `${road} ${dir}`.trim();
            ]]]
          destination: |
            [[[
              const match = entity.attributes.friendly_name ? entity.attributes.friendly_name.match(/to (.*)/i) : null;
              return match ? match[1].toUpperCase() : "";
            ]]]
          minutes: |
            [[[ return Math.round(Number(entity.state)); ]]]
          delay: |
            [[[
              const delay = Number(entity.attributes.delay || 0);
              if (delay <= 0) return "";
              return `+${delay} MIN`;
            ]]]
      - type: custom:button-card
        entity: sensor.the_511_sign_325_i_94_eb_wis_26_to_wis_67
        show_name: false
        show_state: false
        show_icon: false
        tap_action:
          action: more-info
        styles:
          card:
            - background: "#0c0c0c"
            - border: 3px solid "#6a6a6a"
            - border-radius: 3px
            - height: 120px
            - padding: 0
            - overflow: hidden
            - position: relative
          custom_fields:
            header:
              - position: absolute
              - top: 8px
              - left: 0
              - width: 100%
              - text-align: center
              - color: "#ffb300"
              - font-size: 17px
              - font-family: monospace
              - letter-spacing: 4px
              - text-shadow: 0 0 2px rgba(255,176,0,0.75)
            route:
              - position: absolute
              - top: 42px
              - left: 18px
              - color: "#ffb300"
              - font-size: 24px
              - font-family: monospace
              - text-shadow: 0 0 2px rgba(255,176,0,0.75)
            destination:
              - position: absolute
              - top: 78px
              - left: 18px
              - color: "#ffb300"
              - font-size: 27px
              - font-family: monospace
              - text-shadow: 0 0 2px rgba(255,176,0,0.75)
            minutes:
              - position: absolute
              - top: 42px
              - right: 30px
              - color: "#ffb300"
              - font-size: 40px
              - font-family: monospace
              - font-weight: bold
              - line-height: 1
              - text-align: right
              - text-shadow: 0 0 2px rgba(255,176,0,0.75)
            delay:
              - position: absolute
              - top: 95px
              - right: 20px
              - width: 80px
              - text-align: center
              - color: "#ffb300"
              - font-size: 13px
              - font-family: monospace
              - font-weight: bold
              - text-shadow: 0 0 2px rgba(255,176,0,0.75)
        custom_fields:
          header: |
            [[[ return "MINUTES TO"; ]]]
          route: |
            [[[
              const road = entity.attributes.road || "";
              const dirMatch = entity.attributes.friendly_name ? entity.attributes.friendly_name.match(/\b(EB|WB|NB|SB)\b/i) : null;
              const dir = dirMatch ? dirMatch[1].toUpperCase() : "";
              return `${road} ${dir}`.trim();
            ]]]
          destination: |
            [[[
              const match = entity.attributes.friendly_name ? entity.attributes.friendly_name.match(/to (.*)/i) : null;
              return match ? match[1].toUpperCase() : "";
            ]]]
          minutes: |
            [[[ return Math.round(Number(entity.state)); ]]]
          delay: |
            [[[
              const delay = Number(entity.attributes.delay || 0);
              if (delay <= 0) return "";
              return `+${delay} MIN`;
            ]]]
      - type: custom:button-card
        entity: sensor.the_511_sign_311_i_94_eb_gaston_rd_to_wis_26
        show_name: false
        show_state: false
        show_icon: false
        tap_action:
          action: more-info
        styles:
          card:
            - background: "#0c0c0c"
            - border: 3px solid "#6a6a6a"
            - border-radius: 3px
            - height: 120px
            - padding: 0
            - overflow: hidden
            - position: relative
          custom_fields:
            header:
              - position: absolute
              - top: 8px
              - left: 0
              - width: 100%
              - text-align: center
              - color: "#ffb300"
              - font-size: 17px
              - font-family: monospace
              - letter-spacing: 4px
              - text-shadow: 0 0 2px rgba(255,176,0,0.75)
            route:
              - position: absolute
              - top: 42px
              - left: 18px
              - color: "#ffb300"
              - font-size: 24px
              - font-family: monospace
              - text-shadow: 0 0 2px rgba(255,176,0,0.75)
            destination:
              - position: absolute
              - top: 78px
              - left: 18px
              - color: "#ffb300"
              - font-size: 27px
              - font-family: monospace
              - text-shadow: 0 0 2px rgba(255,176,0,0.75)
            minutes:
              - position: absolute
              - top: 42px
              - right: 30px
              - color: "#ffb300"
              - font-size: 40px
              - font-family: monospace
              - font-weight: bold
              - line-height: 1
              - text-align: right
              - text-shadow: 0 0 2px rgba(255,176,0,0.75)
            delay:
              - position: absolute
              - top: 95px
              - right: 20px
              - width: 80px
              - text-align: center
              - color: "#ffb300"
              - font-size: 13px
              - font-family: monospace
              - font-weight: bold
              - text-shadow: 0 0 2px rgba(255,176,0,0.75)
        custom_fields:
          header: |
            [[[ return "MINUTES TO"; ]]]
          route: |
            [[[
              const road = entity.attributes.road || "";
              const dirMatch = entity.attributes.friendly_name ? entity.attributes.friendly_name.match(/\b(EB|WB|NB|SB)\b/i) : null;
              const dir = dirMatch ? dirMatch[1].toUpperCase() : "";
              return `${road} ${dir}`.trim();
            ]]]
          destination: |
            [[[
              const match = entity.attributes.friendly_name ? entity.attributes.friendly_name.match(/to (.*)/i) : null;
              return match ? match[1].toUpperCase() : "";
            ]]]
          minutes: |
            [[[ return Math.round(Number(entity.state)); ]]]
          delay: |
            [[[
              const delay = Number(entity.attributes.delay || 0);
              if (delay <= 0) return "";
              return `+${delay} MIN`;
            ]]]
      - type: custom:button-card
        entity: sensor.the_511_sign_311_i_94_eb_gaston_rd_to_wis_89
        show_name: false
        show_state: false
        show_icon: false
        tap_action:
          action: more-info
        styles:
          card:
            - background: "#0c0c0c"
            - border: 3px solid "#6a6a6a"
            - border-radius: 3px
            - height: 120px
            - padding: 0
            - overflow: hidden
            - position: relative
          custom_fields:
            header:
              - position: absolute
              - top: 8px
              - left: 0
              - width: 100%
              - text-align: center
              - color: "#ffb300"
              - font-size: 17px
              - font-family: monospace
              - letter-spacing: 4px
              - text-shadow: 0 0 2px rgba(255,176,0,0.75)
            route:
              - position: absolute
              - top: 42px
              - left: 18px
              - color: "#ffb300"
              - font-size: 24px
              - font-family: monospace
              - text-shadow: 0 0 2px rgba(255,176,0,0.75)
            destination:
              - position: absolute
              - top: 78px
              - left: 18px
              - color: "#ffb300"
              - font-size: 27px
              - font-family: monospace
              - text-shadow: 0 0 2px rgba(255,176,0,0.75)
            minutes:
              - position: absolute
              - top: 42px
              - right: 30px
              - color: "#ffb300"
              - font-size: 40px
              - font-family: monospace
              - font-weight: bold
              - line-height: 1
              - text-align: right
              - text-shadow: 0 0 2px rgba(255,176,0,0.75)
            delay:
              - position: absolute
              - top: 95px
              - right: 20px
              - width: 80px
              - text-align: center
              - color: "#ffb300"
              - font-size: 13px
              - font-family: monospace
              - font-weight: bold
              - text-shadow: 0 0 2px rgba(255,176,0,0.75)
        custom_fields:
          header: |
            [[[ return "MINUTES TO"; ]]]
          route: |
            [[[
              const road = entity.attributes.road || "";
              const dirMatch = entity.attributes.friendly_name ? entity.attributes.friendly_name.match(/\b(EB|WB|NB|SB)\b/i) : null;
              const dir = dirMatch ? dirMatch[1].toUpperCase() : "";
              return `${road} ${dir}`.trim();
            ]]]
          destination: |
            [[[
              const match = entity.attributes.friendly_name ? entity.attributes.friendly_name.match(/to (.*)/i) : null;
              return match ? match[1].toUpperCase() : "";
            ]]]
          minutes: |
            [[[ return Math.round(Number(entity.state)); ]]]
          delay: |
            [[[
              const delay = Number(entity.attributes.delay || 0);
              if (delay <= 0) return "";
              return `+${delay} MIN`;
            ]]]
      - type: custom:button-card
        entity: sensor.the_511_sign_312_i_94_wb_gaston_rd_to_john_nolen_dr
        show_name: false
        show_state: false
        show_icon: false
        tap_action:
          action: more-info
        styles:
          card:
            - background: "#0c0c0c"
            - border: 3px solid "#6a6a6a"
            - border-radius: 3px
            - height: 120px
            - padding: 0
            - overflow: hidden
            - position: relative
          custom_fields:
            header:
              - position: absolute
              - top: 8px
              - left: 0
              - width: 100%
              - text-align: center
              - color: "#ffb300"
              - font-size: 17px
              - font-family: monospace
              - letter-spacing: 4px
              - text-shadow: 0 0 2px rgba(255,176,0,0.75)
            route:
              - position: absolute
              - top: 42px
              - left: 18px
              - color: "#ffb300"
              - font-size: 24px
              - font-family: monospace
              - text-shadow: 0 0 2px rgba(255,176,0,0.75)
            destination:
              - position: absolute
              - top: 78px
              - left: 18px
              - color: "#ffb300"
              - font-size: 27px
              - font-family: monospace
              - text-shadow: 0 0 2px rgba(255,176,0,0.75)
            minutes:
              - position: absolute
              - top: 42px
              - right: 30px
              - color: "#ffb300"
              - font-size: 40px
              - font-family: monospace
              - font-weight: bold
              - line-height: 1
              - text-align: right
              - text-shadow: 0 0 2px rgba(255,176,0,0.75)
            delay:
              - position: absolute
              - top: 95px
              - right: 20px
              - width: 80px
              - text-align: center
              - color: "#ffb300"
              - font-size: 13px
              - font-family: monospace
              - font-weight: bold
              - text-shadow: 0 0 2px rgba(255,176,0,0.75)
        custom_fields:
          header: |
            [[[ return "MINUTES TO"; ]]]
          route: |
            [[[
              const road = entity.attributes.road || "";
              const dirMatch = entity.attributes.friendly_name ? entity.attributes.friendly_name.match(/\b(EB|WB|NB|SB)\b/i) : null;
              const dir = dirMatch ? dirMatch[1].toUpperCase() : "";
              return `${road} ${dir}`.trim();
            ]]]
          destination: |
            [[[
              const match = entity.attributes.friendly_name ? entity.attributes.friendly_name.match(/to (.*)/i) : null;
              return match ? match[1].toUpperCase() : "";
            ]]]
          minutes: |
            [[[ return Math.round(Number(entity.state)); ]]]
          delay: |
            [[[
              const delay = Number(entity.attributes.delay || 0);
              if (delay <= 0) return "";
              return `+${delay} MIN`;
            ]]]
      - type: custom:button-card
        entity: sensor.the_511_sign_312_i_94_wb_gaston_rd_to_us_12_18
        show_name: false
        show_state: false
        show_icon: false
        tap_action:
          action: more-info
        styles:
          card:
            - background: "#0c0c0c"
            - border: 3px solid "#6a6a6a"
            - border-radius: 3px
            - height: 120px
            - padding: 0
            - overflow: hidden
            - position: relative
          custom_fields:
            header:
              - position: absolute
              - top: 8px
              - left: 0
              - width: 100%
              - text-align: center
              - color: "#ffb300"
              - font-size: 17px
              - font-family: monospace
              - letter-spacing: 4px
              - text-shadow: 0 0 2px rgba(255,176,0,0.75)
            route:
              - position: absolute
              - top: 42px
              - left: 18px
              - color: "#ffb300"
              - font-size: 24px
              - font-family: monospace
              - text-shadow: 0 0 2px rgba(255,176,0,0.75)
            destination:
              - position: absolute
              - top: 78px
              - left: 18px
              - color: "#ffb300"
              - font-size: 27px
              - font-family: monospace
              - text-shadow: 0 0 2px rgba(255,176,0,0.75)
            minutes:
              - position: absolute
              - top: 42px
              - right: 30px
              - color: "#ffb300"
              - font-size: 40px
              - font-family: monospace
              - font-weight: bold
              - line-height: 1
              - text-align: right
              - text-shadow: 0 0 2px rgba(255,176,0,0.75)
            delay:
              - position: absolute
              - top: 95px
              - right: 20px
              - width: 80px
              - text-align: center
              - color: "#ffb300"
              - font-size: 13px
              - font-family: monospace
              - font-weight: bold
              - text-shadow: 0 0 2px rgba(255,176,0,0.75)
        custom_fields:
          header: |
            [[[ return "MINUTES TO"; ]]]
          route: |
            [[[
              const road = entity.attributes.road || "";
              const dirMatch = entity.attributes.friendly_name ? entity.attributes.friendly_name.match(/\b(EB|WB|NB|SB)\b/i) : null;
              const dir = dirMatch ? dirMatch[1].toUpperCase() : "";
              return `${road} ${dir}`.trim();
            ]]]
          destination: |
            [[[
              const match = entity.attributes.friendly_name ? entity.attributes.friendly_name.match(/to (.*)/i) : null;
              return match ? match[1].toUpperCase() : "";
            ]]]
          minutes: |
            [[[ return Math.round(Number(entity.state)); ]]]
          delay: |
            [[[
              const delay = Number(entity.attributes.delay || 0);
              if (delay <= 0) return "";
              return `+${delay} MIN`;
            ]]]
      - type: custom:button-card
        entity: sensor.the_511_sign_312_i_94_wb_gaston_rd_to_wis_19
        show_name: false
        show_state: false
        show_icon: false
        tap_action:
          action: more-info
        styles:
          card:
            - background: "#0c0c0c"
            - border: 3px solid "#6a6a6a"
            - border-radius: 3px
            - height: 120px
            - padding: 0
            - overflow: hidden
            - position: relative
          custom_fields:
            header:
              - position: absolute
              - top: 8px
              - left: 0
              - width: 100%
              - text-align: center
              - color: "#ffb300"
              - font-size: 17px
              - font-family: monospace
              - letter-spacing: 4px
              - text-shadow: 0 0 2px rgba(255,176,0,0.75)
            route:
              - position: absolute
              - top: 42px
              - left: 18px
              - color: "#ffb300"
              - font-size: 24px
              - font-family: monospace
              - text-shadow: 0 0 2px rgba(255,176,0,0.75)
            destination:
              - position: absolute
              - top: 78px
              - left: 18px
              - color: "#ffb300"
              - font-size: 27px
              - font-family: monospace
              - text-shadow: 0 0 2px rgba(255,176,0,0.75)
            minutes:
              - position: absolute
              - top: 42px
              - right: 30px
              - color: "#ffb300"
              - font-size: 40px
              - font-family: monospace
              - font-weight: bold
              - line-height: 1
              - text-align: right
              - text-shadow: 0 0 2px rgba(255,176,0,0.75)
            delay:
              - position: absolute
              - top: 95px
              - right: 20px
              - width: 80px
              - text-align: center
              - color: "#ffb300"
              - font-size: 13px
              - font-family: monospace
              - font-weight: bold
              - text-shadow: 0 0 2px rgba(255,176,0,0.75)
        custom_fields:
          header: |
            [[[ return "MINUTES TO"; ]]]
          route: |
            [[[
              const road = entity.attributes.road || "";
              const dirMatch = entity.attributes.friendly_name ? entity.attributes.friendly_name.match(/\b(EB|WB|NB|SB)\b/i) : null;
              const dir = dirMatch ? dirMatch[1].toUpperCase() : "";
              return `${road} ${dir}`.trim();
            ]]]
          destination: |
            [[[
              const match = entity.attributes.friendly_name ? entity.attributes.friendly_name.match(/to (.*)/i) : null;
              return match ? match[1].toUpperCase() : "";
            ]]]
          minutes: |
            [[[ return Math.round(Number(entity.state)); ]]]
          delay: |
            [[[
              const delay = Number(entity.attributes.delay || 0);
              if (delay <= 0) return "";
              return `+${delay} MIN`;
            ]]]
      - type: custom:button-card
        entity: sensor.the_511_sign_305_i_39_90_94_sb_us_151_to_us_12_18
        show_name: false
        show_state: false
        show_icon: false
        tap_action:
          action: more-info
        styles:
          card:
            - background: "#0c0c0c"
            - border: 3px solid "#6a6a6a"
            - border-radius: 3px
            - height: 120px
            - padding: 0
            - overflow: hidden
            - position: relative
          custom_fields:
            header:
              - position: absolute
              - top: 8px
              - left: 0
              - width: 100%
              - text-align: center
              - color: "#ffb300"
              - font-size: 17px
              - font-family: monospace
              - letter-spacing: 4px
              - text-shadow: 0 0 2px rgba(255,176,0,0.75)
            route:
              - position: absolute
              - top: 42px
              - left: 18px
              - color: "#ffb300"
              - font-size: 24px
              - font-family: monospace
              - text-shadow: 0 0 2px rgba(255,176,0,0.75)
            destination:
              - position: absolute
              - top: 78px
              - left: 18px
              - color: "#ffb300"
              - font-size: 27px
              - font-family: monospace
              - text-shadow: 0 0 2px rgba(255,176,0,0.75)
            minutes:
              - position: absolute
              - top: 42px
              - right: 30px
              - color: "#ffb300"
              - font-size: 40px
              - font-family: monospace
              - font-weight: bold
              - line-height: 1
              - text-align: right
              - text-shadow: 0 0 2px rgba(255,176,0,0.75)
            delay:
              - position: absolute
              - top: 95px
              - right: 20px
              - width: 80px
              - text-align: center
              - color: "#ffb300"
              - font-size: 13px
              - font-family: monospace
              - font-weight: bold
              - text-shadow: 0 0 2px rgba(255,176,0,0.75)
        custom_fields:
          header: |
            [[[ return "MINUTES TO"; ]]]
          route: |
            [[[
              const road = entity.attributes.road || "";
              const dirMatch = entity.attributes.friendly_name ? entity.attributes.friendly_name.match(/\b(EB|WB|NB|SB)\b/i) : null;
              const dir = dirMatch ? dirMatch[1].toUpperCase() : "";
              return `${road} ${dir}`.trim();
            ]]]
          destination: |
            [[[
              const match = entity.attributes.friendly_name ? entity.attributes.friendly_name.match(/to (.*)/i) : null;
              return match ? match[1].toUpperCase() : "";
            ]]]
          minutes: |
            [[[ return Math.round(Number(entity.state)); ]]]
          delay: |
            [[[
              const delay = Number(entity.attributes.delay || 0);
              if (delay <= 0) return "";
              return `+${delay} MIN`;
            ]]]
      - type: custom:button-card
        entity: sensor.the_511_sign_328_i_39_90_94_sb_lein_rd_to_i_94_at_county_n
        show_name: false
        show_state: false
        show_icon: false
        tap_action:
          action: more-info
        styles:
          card:
            - background: "#0c0c0c"
            - border: 3px solid "#6a6a6a"
            - border-radius: 3px
            - height: 120px
            - padding: 0
            - overflow: hidden
            - position: relative
          custom_fields:
            header:
              - position: absolute
              - top: 8px
              - left: 0
              - width: 100%
              - text-align: center
              - color: "#ffb300"
              - font-size: 17px
              - font-family: monospace
              - letter-spacing: 4px
              - text-shadow: 0 0 2px rgba(255,176,0,0.75)
            route:
              - position: absolute
              - top: 42px
              - left: 18px
              - color: "#ffb300"
              - font-size: 24px
              - font-family: monospace
              - text-shadow: 0 0 2px rgba(255,176,0,0.75)
            destination:
              - position: absolute
              - top: 78px
              - left: 18px
              - color: "#ffb300"
              - font-size: 27px
              - font-family: monospace
              - text-shadow: 0 0 2px rgba(255,176,0,0.75)
            minutes:
              - position: absolute
              - top: 42px
              - right: 30px
              - color: "#ffb300"
              - font-size: 40px
              - font-family: monospace
              - font-weight: bold
              - line-height: 1
              - text-align: right
              - text-shadow: 0 0 2px rgba(255,176,0,0.75)
            delay:
              - position: absolute
              - top: 95px
              - right: 20px
              - width: 80px
              - text-align: center
              - color: "#ffb300"
              - font-size: 13px
              - font-family: monospace
              - font-weight: bold
              - text-shadow: 0 0 2px rgba(255,176,0,0.75)
        custom_fields:
          header: |
            [[[ return "MINUTES TO"; ]]]
          route: |
            [[[
              const road = entity.attributes.road || "";
              const dirMatch = entity.attributes.friendly_name ? entity.attributes.friendly_name.match(/\b(EB|WB|NB|SB)\b/i) : null;
              const dir = dirMatch ? dirMatch[1].toUpperCase() : "";
              return `${road} ${dir}`.trim();
            ]]]
          destination: |
            [[[
              const match = entity.attributes.friendly_name ? entity.attributes.friendly_name.match(/to (.*)/i) : null;
              return match ? match[1].toUpperCase() : "";
            ]]]
          minutes: |
            [[[ return Math.round(Number(entity.state)); ]]]
          delay: |
            [[[
              const delay = Number(entity.attributes.delay || 0);
              if (delay <= 0) return "";
              return `+${delay} MIN`;
            ]]]
      - type: custom:button-card
        entity: sensor.the_511_sign_328_i_39_90_94_sb_lein_rd_to_us_12_18
        show_name: false
        show_state: false
        show_icon: false
        tap_action:
          action: more-info
        styles:
          card:
            - background: "#0c0c0c"
            - border: 3px solid "#6a6a6a"
            - border-radius: 3px
            - height: 120px
            - padding: 0
            - overflow: hidden
            - position: relative
          custom_fields:
            header:
              - position: absolute
              - top: 8px
              - left: 0
              - width: 100%
              - text-align: center
              - color: "#ffb300"
              - font-size: 17px
              - font-family: monospace
              - letter-spacing: 4px
              - text-shadow: 0 0 2px rgba(255,176,0,0.75)
            route:
              - position: absolute
              - top: 42px
              - left: 18px
              - color: "#ffb300"
              - font-size: 24px
              - font-family: monospace
              - text-shadow: 0 0 2px rgba(255,176,0,0.75)
            destination:
              - position: absolute
              - top: 78px
              - left: 18px
              - color: "#ffb300"
              - font-size: 27px
              - font-family: monospace
              - text-shadow: 0 0 2px rgba(255,176,0,0.75)
            minutes:
              - position: absolute
              - top: 42px
              - right: 30px
              - color: "#ffb300"
              - font-size: 40px
              - font-family: monospace
              - font-weight: bold
              - line-height: 1
              - text-align: right
              - text-shadow: 0 0 2px rgba(255,176,0,0.75)
            delay:
              - position: absolute
              - top: 95px
              - right: 20px
              - width: 80px
              - text-align: center
              - color: "#ffb300"
              - font-size: 13px
              - font-family: monospace
              - font-weight: bold
              - text-shadow: 0 0 2px rgba(255,176,0,0.75)
        custom_fields:
          header: |
            [[[ return "MINUTES TO"; ]]]
          route: |
            [[[
              const road = entity.attributes.road || "";
              const dirMatch = entity.attributes.friendly_name ? entity.attributes.friendly_name.match(/\b(EB|WB|NB|SB)\b/i) : null;
              const dir = dirMatch ? dirMatch[1].toUpperCase() : "";
              return `${road} ${dir}`.trim();
            ]]]
          destination: |
            [[[
              const match = entity.attributes.friendly_name ? entity.attributes.friendly_name.match(/to (.*)/i) : null;
              return match ? match[1].toUpperCase() : "";
            ]]]
          minutes: |
            [[[ return Math.round(Number(entity.state)); ]]]
          delay: |
            [[[
              const delay = Number(entity.attributes.delay || 0);
              if (delay <= 0) return "";
              return `+${delay} MIN`;
            ]]]
      - type: custom:button-card
        entity: sensor.the_511_sign_328_i_39_90_94_sb_lein_rd_to_us_12_18_at_park_st
        show_name: false
        show_state: false
        show_icon: false
        tap_action:
          action: more-info
        styles:
          card:
            - background: "#0c0c0c"
            - border: 3px solid "#6a6a6a"
            - border-radius: 3px
            - height: 120px
            - padding: 0
            - overflow: hidden
            - position: relative
          custom_fields:
            header:
              - position: absolute
              - top: 8px
              - left: 0
              - width: 100%
              - text-align: center
              - color: "#ffb300"
              - font-size: 17px
              - font-family: monospace
              - letter-spacing: 4px
              - text-shadow: 0 0 2px rgba(255,176,0,0.75)
            route:
              - position: absolute
              - top: 42px
              - left: 18px
              - color: "#ffb300"
              - font-size: 24px
              - font-family: monospace
              - text-shadow: 0 0 2px rgba(255,176,0,0.75)
            destination:
              - position: absolute
              - top: 78px
              - left: 18px
              - color: "#ffb300"
              - font-size: 27px
              - font-family: monospace
              - text-shadow: 0 0 2px rgba(255,176,0,0.75)
            minutes:
              - position: absolute
              - top: 42px
              - right: 30px
              - color: "#ffb300"
              - font-size: 40px
              - font-family: monospace
              - font-weight: bold
              - line-height: 1
              - text-align: right
              - text-shadow: 0 0 2px rgba(255,176,0,0.75)
            delay:
              - position: absolute
              - top: 95px
              - right: 20px
              - width: 80px
              - text-align: center
              - color: "#ffb300"
              - font-size: 13px
              - font-family: monospace
              - font-weight: bold
              - text-shadow: 0 0 2px rgba(255,176,0,0.75)
        custom_fields:
          header: |
            [[[ return "MINUTES TO"; ]]]
          route: |
            [[[
              const road = entity.attributes.road || "";
              const dirMatch = entity.attributes.friendly_name ? entity.attributes.friendly_name.match(/\b(EB|WB|NB|SB)\b/i) : null;
              const dir = dirMatch ? dirMatch[1].toUpperCase() : "";
              return `${road} ${dir}`.trim();
            ]]]
          destination: |
            [[[
              const match = entity.attributes.friendly_name ? entity.attributes.friendly_name.match(/to (.*)/i) : null;
              return match ? match[1].toUpperCase() : "";
            ]]]
          minutes: |
            [[[ return Math.round(Number(entity.state)); ]]]
          delay: |
            [[[
              const delay = Number(entity.attributes.delay || 0);
              if (delay <= 0) return "";
              return `+${delay} MIN`;
            ]]]
      - type: custom:button-card
        entity: sensor.the_511_sign_339_i_39_90_nb_church_st_to_i_94
        show_name: false
        show_state: false
        show_icon: false
        tap_action:
          action: more-info
        styles:
          card:
            - background: "#0c0c0c"
            - border: 3px solid "#6a6a6a"
            - border-radius: 3px
            - height: 120px
            - padding: 0
            - overflow: hidden
            - position: relative
          custom_fields:
            header:
              - position: absolute
              - top: 8px
              - left: 0
              - width: 100%
              - text-align: center
              - color: "#ffb300"
              - font-size: 17px
              - font-family: monospace
              - letter-spacing: 4px
              - text-shadow: 0 0 2px rgba(255,176,0,0.75)
            route:
              - position: absolute
              - top: 42px
              - left: 18px
              - color: "#ffb300"
              - font-size: 24px
              - font-family: monospace
              - text-shadow: 0 0 2px rgba(255,176,0,0.75)
            destination:
              - position: absolute
              - top: 78px
              - left: 18px
              - color: "#ffb300"
              - font-size: 27px
              - font-family: monospace
              - text-shadow: 0 0 2px rgba(255,176,0,0.75)
            minutes:
              - position: absolute
              - top: 42px
              - right: 30px
              - color: "#ffb300"
              - font-size: 40px
              - font-family: monospace
              - font-weight: bold
              - line-height: 1
              - text-align: right
              - text-shadow: 0 0 2px rgba(255,176,0,0.75)
            delay:
              - position: absolute
              - top: 95px
              - right: 20px
              - width: 80px
              - text-align: center
              - color: "#ffb300"
              - font-size: 13px
              - font-family: monospace
              - font-weight: bold
              - text-shadow: 0 0 2px rgba(255,176,0,0.75)
        custom_fields:
          header: |
            [[[ return "MINUTES TO"; ]]]
          route: |
            [[[
              const road = entity.attributes.road || "";
              const dirMatch = entity.attributes.friendly_name ? entity.attributes.friendly_name.match(/\b(EB|WB|NB|SB)\b/i) : null;
              const dir = dirMatch ? dirMatch[1].toUpperCase() : "";
              return `${road} ${dir}`.trim();
            ]]]
          destination: |
            [[[
              const match = entity.attributes.friendly_name ? entity.attributes.friendly_name.match(/to (.*)/i) : null;
              return match ? match[1].toUpperCase() : "";
            ]]]
          minutes: |
            [[[ return Math.round(Number(entity.state)); ]]]
          delay: |
            [[[
              const delay = Number(entity.attributes.delay || 0);
              if (delay <= 0) return "";
              return `+${delay} MIN`;
            ]]]
      - type: custom:button-card
        entity: sensor.the_511_sign_339_i_39_90_nb_church_st_to_us_12_18
        show_name: false
        show_state: false
        show_icon: false
        tap_action:
          action: more-info
        styles:
          card:
            - background: "#0c0c0c"
            - border: 3px solid "#6a6a6a"
            - border-radius: 3px
            - height: 120px
            - padding: 0
            - overflow: hidden
            - position: relative
          custom_fields:
            header:
              - position: absolute
              - top: 8px
              - left: 0
              - width: 100%
              - text-align: center
              - color: "#ffb300"
              - font-size: 17px
              - font-family: monospace
              - letter-spacing: 4px
              - text-shadow: 0 0 2px rgba(255,176,0,0.75)
            route:
              - position: absolute
              - top: 42px
              - left: 18px
              - color: "#ffb300"
              - font-size: 24px
              - font-family: monospace
              - text-shadow: 0 0 2px rgba(255,176,0,0.75)
            destination:
              - position: absolute
              - top: 78px
              - left: 18px
              - color: "#ffb300"
              - font-size: 27px
              - font-family: monospace
              - text-shadow: 0 0 2px rgba(255,176,0,0.75)
            minutes:
              - position: absolute
              - top: 42px
              - right: 30px
              - color: "#ffb300"
              - font-size: 40px
              - font-family: monospace
              - font-weight: bold
              - line-height: 1
              - text-align: right
              - text-shadow: 0 0 2px rgba(255,176,0,0.75)
            delay:
              - position: absolute
              - top: 95px
              - right: 20px
              - width: 80px
              - text-align: center
              - color: "#ffb300"
              - font-size: 13px
              - font-family: monospace
              - font-weight: bold
              - text-shadow: 0 0 2px rgba(255,176,0,0.75)
        custom_fields:
          header: |
            [[[ return "MINUTES TO"; ]]]
          route: |
            [[[
              const road = entity.attributes.road || "";
              const dirMatch = entity.attributes.friendly_name ? entity.attributes.friendly_name.match(/\b(EB|WB|NB|SB)\b/i) : null;
              const dir = dirMatch ? dirMatch[1].toUpperCase() : "";
              return `${road} ${dir}`.trim();
            ]]]
          destination: |
            [[[
              const match = entity.attributes.friendly_name ? entity.attributes.friendly_name.match(/to (.*)/i) : null;
              return match ? match[1].toUpperCase() : "";
            ]]]
          minutes: |
            [[[ return Math.round(Number(entity.state)); ]]]
          delay: |
            [[[
              const delay = Number(entity.attributes.delay || 0);
              if (delay <= 0) return "";
              return `+${delay} MIN`;
            ]]]
      - type: custom:button-card
        entity: sensor.the_511_sign_326_i_94_wb_wis_26_to_i_39_90
        show_name: false
        show_state: false
        show_icon: false
        tap_action:
          action: more-info
        styles:
          card:
            - background: "#0c0c0c"
            - border: 3px solid "#6a6a6a"
            - border-radius: 3px
            - height: 120px
            - padding: 0
            - overflow: hidden
            - position: relative
          custom_fields:
            header:
              - position: absolute
              - top: 8px
              - left: 0
              - width: 100%
              - text-align: center
              - color: "#ffb300"
              - font-size: 17px
              - font-family: monospace
              - letter-spacing: 4px
              - text-shadow: 0 0 2px rgba(255,176,0,0.75)
            route:
              - position: absolute
              - top: 42px
              - left: 18px
              - color: "#ffb300"
              - font-size: 24px
              - font-family: monospace
              - text-shadow: 0 0 2px rgba(255,176,0,0.75)
            destination:
              - position: absolute
              - top: 78px
              - left: 18px
              - color: "#ffb300"
              - font-size: 27px
              - font-family: monospace
              - text-shadow: 0 0 2px rgba(255,176,0,0.75)
            minutes:
              - position: absolute
              - top: 42px
              - right: 30px
              - color: "#ffb300"
              - font-size: 40px
              - font-family: monospace
              - font-weight: bold
              - line-height: 1
              - text-align: right
              - text-shadow: 0 0 2px rgba(255,176,0,0.75)
            delay:
              - position: absolute
              - top: 95px
              - right: 20px
              - width: 80px
              - text-align: center
              - color: "#ffb300"
              - font-size: 13px
              - font-family: monospace
              - font-weight: bold
              - text-shadow: 0 0 2px rgba(255,176,0,0.75)
        custom_fields:
          header: |
            [[[ return "MINUTES TO"; ]]]
          route: |
            [[[
              const road = entity.attributes.road || "";
              const dirMatch = entity.attributes.friendly_name ? entity.attributes.friendly_name.match(/\b(EB|WB|NB|SB)\b/i) : null;
              const dir = dirMatch ? dirMatch[1].toUpperCase() : "";
              return `${road} ${dir}`.trim();
            ]]]
          destination: |
            [[[
              const match = entity.attributes.friendly_name ? entity.attributes.friendly_name.match(/to (.*)/i) : null;
              return match ? match[1].toUpperCase() : "";
            ]]]
          minutes: |
            [[[ return Math.round(Number(entity.state)); ]]]
          delay: |
            [[[
              const delay = Number(entity.attributes.delay || 0);
              if (delay <= 0) return "";
              return `+${delay} MIN`;
            ]]]
      - type: custom:button-card
        entity: sensor.the_511_sign_326_i_94_wb_wis_26_to_wis_73
        show_name: false
        show_state: false
        show_icon: false
        tap_action:
          action: more-info
        styles:
          card:
            - background: "#0c0c0c"
            - border: 3px solid "#6a6a6a"
            - border-radius: 3px
            - height: 120px
            - padding: 0
            - overflow: hidden
            - position: relative
          custom_fields:
            header:
              - position: absolute
              - top: 8px
              - left: 0
              - width: 100%
              - text-align: center
              - color: "#ffb300"
              - font-size: 17px
              - font-family: monospace
              - letter-spacing: 4px
              - text-shadow: 0 0 2px rgba(255,176,0,0.75)
            route:
              - position: absolute
              - top: 42px
              - left: 18px
              - color: "#ffb300"
              - font-size: 24px
              - font-family: monospace
              - text-shadow: 0 0 2px rgba(255,176,0,0.75)
            destination:
              - position: absolute
              - top: 78px
              - left: 18px
              - color: "#ffb300"
              - font-size: 27px
              - font-family: monospace
              - text-shadow: 0 0 2px rgba(255,176,0,0.75)
            minutes:
              - position: absolute
              - top: 42px
              - right: 30px
              - color: "#ffb300"
              - font-size: 40px
              - font-family: monospace
              - font-weight: bold
              - line-height: 1
              - text-align: right
              - text-shadow: 0 0 2px rgba(255,176,0,0.75)
            delay:
              - position: absolute
              - top: 95px
              - right: 20px
              - width: 80px
              - text-align: center
              - color: "#ffb300"
              - font-size: 13px
              - font-family: monospace
              - font-weight: bold
              - text-shadow: 0 0 2px rgba(255,176,0,0.75)
        custom_fields:
          header: |
            [[[ return "MINUTES TO"; ]]]
          route: |
            [[[
              const road = entity.attributes.road || "";
              const dirMatch = entity.attributes.friendly_name ? entity.attributes.friendly_name.match(/\b(EB|WB|NB|SB)\b/i) : null;
              const dir = dirMatch ? dirMatch[1].toUpperCase() : "";
              return `${road} ${dir}`.trim();
            ]]]
          destination: |
            [[[
              const match = entity.attributes.friendly_name ? entity.attributes.friendly_name.match(/to (.*)/i) : null;
              return match ? match[1].toUpperCase() : "";
            ]]]
          minutes: |
            [[[ return Math.round(Number(entity.state)); ]]]
          delay: |
            [[[
              const delay = Number(entity.attributes.delay || 0);
              if (delay <= 0) return "";
              return `+${delay} MIN`;
            ]]]
      - type: custom:button-card
        entity: sensor.the_511_sign_344_i_39_90_sb_cottage_grove_rd_to_wis_73
        show_name: false
        show_state: false
        show_icon: false
        tap_action:
          action: more-info
        styles:
          card:
            - background: "#0c0c0c"
            - border: 3px solid "#6a6a6a"
            - border-radius: 3px
            - height: 120px
            - padding: 0
            - overflow: hidden
            - position: relative
          custom_fields:
            header:
              - position: absolute
              - top: 8px
              - left: 0
              - width: 100%
              - text-align: center
              - color: "#ffb300"
              - font-size: 17px
              - font-family: monospace
              - letter-spacing: 4px
              - text-shadow: 0 0 2px rgba(255,176,0,0.75)
            route:
              - position: absolute
              - top: 42px
              - left: 18px
              - color: "#ffb300"
              - font-size: 24px
              - font-family: monospace
              - text-shadow: 0 0 2px rgba(255,176,0,0.75)
            destination:
              - position: absolute
              - top: 78px
              - left: 18px
              - color: "#ffb300"
              - font-size: 27px
              - font-family: monospace
              - text-shadow: 0 0 2px rgba(255,176,0,0.75)
            minutes:
              - position: absolute
              - top: 42px
              - right: 30px
              - color: "#ffb300"
              - font-size: 40px
              - font-family: monospace
              - font-weight: bold
              - line-height: 1
              - text-align: right
              - text-shadow: 0 0 2px rgba(255,176,0,0.75)
            delay:
              - position: absolute
              - top: 95px
              - right: 20px
              - width: 80px
              - text-align: center
              - color: "#ffb300"
              - font-size: 13px
              - font-family: monospace
              - font-weight: bold
              - text-shadow: 0 0 2px rgba(255,176,0,0.75)
        custom_fields:
          header: |
            [[[ return "MINUTES TO"; ]]]
          route: |
            [[[
              const road = entity.attributes.road || "";
              const dirMatch = entity.attributes.friendly_name ? entity.attributes.friendly_name.match(/\b(EB|WB|NB|SB)\b/i) : null;
              const dir = dirMatch ? dirMatch[1].toUpperCase() : "";
              return `${road} ${dir}`.trim();
            ]]]
          destination: |
            [[[
              const match = entity.attributes.friendly_name ? entity.attributes.friendly_name.match(/to (.*)/i) : null;
              return match ? match[1].toUpperCase() : "";
            ]]]
          minutes: |
            [[[ return Math.round(Number(entity.state)); ]]]
          delay: |
            [[[
              const delay = Number(entity.attributes.delay || 0);
              if (delay <= 0) return "";
              return `+${delay} MIN`;
            ]]]
      - type: custom:button-card
        entity: sensor.the_511_sign_343_i_39_90_nb_cottage_grove_rd_to_us_151
        show_name: false
        show_state: false
        show_icon: false
        tap_action:
          action: more-info
        styles:
          card:
            - background: "#0c0c0c"
            - border: 3px solid "#6a6a6a"
            - border-radius: 3px
            - height: 120px
            - padding: 0
            - overflow: hidden
            - position: relative
          custom_fields:
            header:
              - position: absolute
              - top: 8px
              - left: 0
              - width: 100%
              - text-align: center
              - color: "#ffb300"
              - font-size: 17px
              - font-family: monospace
              - letter-spacing: 4px
              - text-shadow: 0 0 2px rgba(255,176,0,0.75)
            route:
              - position: absolute
              - top: 42px
              - left: 18px
              - color: "#ffb300"
              - font-size: 24px
              - font-family: monospace
              - text-shadow: 0 0 2px rgba(255,176,0,0.75)
            destination:
              - position: absolute
              - top: 78px
              - left: 18px
              - color: "#ffb300"
              - font-size: 27px
              - font-family: monospace
              - text-shadow: 0 0 2px rgba(255,176,0,0.75)
            minutes:
              - position: absolute
              - top: 42px
              - right: 30px
              - color: "#ffb300"
              - font-size: 40px
              - font-family: monospace
              - font-weight: bold
              - line-height: 1
              - text-align: right
              - text-shadow: 0 0 2px rgba(255,176,0,0.75)
            delay:
              - position: absolute
              - top: 95px
              - right: 20px
              - width: 80px
              - text-align: center
              - color: "#ffb300"
              - font-size: 13px
              - font-family: monospace
              - font-weight: bold
              - text-shadow: 0 0 2px rgba(255,176,0,0.75)
        custom_fields:
          header: |
            [[[ return "MINUTES TO"; ]]]
          route: |
            [[[
              const road = entity.attributes.road || "";
              const dirMatch = entity.attributes.friendly_name ? entity.attributes.friendly_name.match(/\b(EB|WB|NB|SB)\b/i) : null;
              const dir = dirMatch ? dirMatch[1].toUpperCase() : "";
              return `${road} ${dir}`.trim();
            ]]]
          destination: |
            [[[
              const match = entity.attributes.friendly_name ? entity.attributes.friendly_name.match(/to (.*)/i) : null;
              return match ? match[1].toUpperCase() : "";
            ]]]
          minutes: |
            [[[ return Math.round(Number(entity.state)); ]]]
          delay: |
            [[[
              const delay = Number(entity.attributes.delay || 0);
              if (delay <= 0) return "";
              return `+${delay} MIN`;
            ]]]
button_type: name
sub_button:
  main: []
  bottom: []
show_header: true
popup_style: classic
```

</details>

## Travel times

![Travel times card](dashboard/screenshots/travel_times.png)

A travel-time card for the configured routes: each row shows the route
name, a delay status line (green/amber/red), and the rounded minutes to
destination, colored amber.

<details>
<summary>Card YAML</summary>

```yaml
type: custom:button-card
name: |
  [[[
    return `
      <div style="display:flex;align-items:center;gap:10px;">
        <img src="/local/travel_times.png"
             style="width:50px;height:50px;">
        <span>Current Travel Times</span>
      </div>
    `;
  ]]]
show_icon: false
triggers_update:
  - sensor.the_511_i_94_wb_wis_73_to_i_39_90
  - sensor.the_511_i_94_eb_wis_73_to_wis_26
  - sensor.the_511_i_94_eb_wis_26_to_wis_67
  - sensor.the_511_i_94_wb_wis_26_to_wis_73
  - sensor.the_511_i_94_eb_i_39_90_to_wis_73
  - sensor.the_511_wis_30_wb_i_39_90_to_e_washington_ave
  - sensor.the_511_i_39_90_94_nb_badger_interchange_to_us_51
  - sensor.the_511_i_39_90_sb_badger_interchange_to_us_12_18
custom_fields:
  traffic_list: |
    [[[
      const sensors = [
        'sensor.the_511_i_39_90_94_nb_badger_interchange_to_us_51',
        'sensor.the_511_i_39_90_sb_badger_interchange_to_us_12_18',
        'sensor.the_511_i_94_eb_wis_73_to_wis_26',
        'sensor.the_511_i_94_eb_wis_26_to_wis_67',
        'sensor.the_511_i_94_eb_i_39_90_to_wis_73',
        'sensor.the_511_i_94_wb_wis_26_to_wis_73',
        'sensor.the_511_i_94_wb_wis_73_to_i_39_90',
        'sensor.the_511_wis_30_wb_i_39_90_to_e_washington_ave'
      ];

      const rows = sensors.map(id => {
        const ent = states[id];
        if (!ent) return '';

        // 1. Clean up route name
        let rawName = ent.attributes.friendly_name || id;
        let cleanName = rawName
          .replace(/^The\s+511\s+/i, '')
          .replace(/\s+to\s+/i, ' → ');

        // 2. Convert state to a rounded whole number
        const rawState = parseFloat(ent.state);
        const state = isNaN(rawState) ? ent.state : Math.round(rawState);
        const unit = ent.attributes.unit_of_measurement === 'min' ? 'm' : (ent.attributes.unit_of_measurement || 'm');

        // 3. Logic for the secondary status delay line
        const delay = Math.round(parseFloat(ent.attributes.delay)) || 0;
        let statusText = '';

        if (delay === 0) {
          statusText = '🟢 Traffic flowing normally';
        } else if (delay < 5) {
          statusText = `🟡 ${delay} minute delay`;
        } else {
          statusText = `🔴 Heavy traffic ${delay} minute delay`;
        }

        return `
          <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid rgba(255,255,255,0.08); padding: 8px 0;">
            <div style="display: flex; flex-direction: column; text-align: left;">
              <span style="font-size: 14px; font-weight: 500; color: #E0E0E0;">${cleanName}</span>
              <span style="font-size: 11px; opacity: 0.75; margin-top: 2px;">${statusText}</span>
            </div>
            <span style="font-size: 15px; font-weight: bold; color: #FFC107; margin-left: 12px; white-space: nowrap;">${state}${unit}</span>
          </div>
        `;
      }).join('');

      return `<div style="display: flex; flex-direction: column; width: 100%;">${rows}</div>`;
    ]]]
styles:
  card:
    - background-color: null
    - border-radius: 12px
    - padding: 18px 16px
  grid:
    - grid-template-areas: "\"n\" \"traffic_list\""
    - grid-template-columns: 1fr
  name:
    - font-weight: 800
    - font-size: 20px
    - color: "#FFC107"
    - justify-self: start
    - margin-bottom: 8px
  custom_fields:
    traffic_list:
```

</details>


