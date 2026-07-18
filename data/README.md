# Data Dictionary

`infections.csv` contains aggregated workplace respiratory infection records across a hospital network.

| Column | Description |
| --- | --- |
| `record_id` | Unique row identifier. |
| `infections` | Count of respiratory infections recorded for the group. |
| `ppe_regime` | PPE protocol category, coded from 1 to 4. |
| `experience` | Nursing experience category, coded from 1 to 4. |
| `hours` | Total hours worked by the group; used as the exposure offset. |
| `training` | Proportion of staff who completed external infection-control training. |
| `wage_inc` | Proportion of staff who received a wage increase in the prior year. |

The modelling workflow derives `infection_rate`, measured as infections per 1,000 worked hours.
