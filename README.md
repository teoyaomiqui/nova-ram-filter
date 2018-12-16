# Nova Actual Resource Filter
Used with openstack nova scheduler

## Filter purpose:
1) Filter out hosts from scheduling instances on them based on actual host resource utilisation.
2) Use 3rd party metrics to descide wether to schedule instance on nova hypervisors

## Supported metric sources:
1) Currently the only source for metrics is prometheus

## Metrics supported available:
### Filter was tested with the following metrics:
`cpu_usage_idle` and `mem_used_percent`, these are default metrics.

any metric other could be used as long as driver supports it. The function for metrics to be evaluated against in prometheus is `avg_over_time`


## Additional bahavior:
If filter fails, at any stipulated reason, host should pass, and instance will be able to be scheduled on it.

## Possible problems with the filter.

1) Prometheus taking too long to response: you should consider increasing timeout in prometheus driver options, in config
2) Prometheus is not reachable at all: Make sure you have correct prometheus endpoint configured, default one is dns name `mtr`

## Installation instructions, for MCP:
### Prerequisites:
1) Access to salt master with root priviliges
2) Access to reclass

### Instructions:
Note: procedure is not automated, so there are manual steps to be done:
The deployment procedure is not fully automated and some steps have to be done manually:

name of the env should be either itcc or jeddah

```bash
salt ctl* cmd.run 'apt install -y git && git clone --single-branch -b <name of the env> <path_to_git_repository> /usr/lib/python2.7/dist-packages/stc_nova_filters'
```
verify that repository is cloned and is correct branch:

```bash
salt ctl* cmd.run 'cd /usr/lib/python2.7/dist-packages/stc_nova_filters && ls -la && git branch -va'
```
edit reclass git repository, file classes/cluster/<cluster_name>/openstack/control.yml:
```yaml

scheduler_custom_filters:
- stcs.aggregate_image_jail.AggregateImageJail
- stc_nova_filters.resource_filter.ActualResourceFilter
scheduler_default_filters: "DifferentHostFilter,SameHostFilter,RetryFilter,AvailabilityZoneFilter,RamFilter,CoreFilter,DiskFilter,ComputeFilter,ComputeCapabilitiesFilter,ImagePropertiesFilter,ServerGroupAntiAffinityFilter,ServerGroupAffinityFilter,PciPassthroughFilter,NUMATopologyFilter,AggregateInstanceExtraSpecsFilter,AggregateImageJail,ActualResourceFilter"
```
apply changes to nova scheduler:

```bash
salt ctl* state.sls nova.controller -b 1 test=true
salt ctl* state.sls nova.controller -b 1
```

verify that changes are correct, and run without test=true note: the state can take a long time to run, due to nova cells command in it, versions of ocata and above


## How to configure filter:
Currently MCP does not support custom changes to /etc/nova/nova.conf file, so in the deployments, i recommend, changing default values in filter code, and using specific branch for each env
For example, in Jeddah you can have threshold = 80.0 for mem_used_percent metric to, and in itcc it can be threshold = 90. To deal with this, we have two branches:
1) `itcc` branch
2) `jeddah` branch

### Instructions:
1) Clone repository on your pc and checkout correct branch:
```bash
git clone <this_repo_url>
git checkout -b origin/<branch_name>

```
In this git repo, open file resource_filter.py, find mem_used_percent_options_dict, and 
2) modify it with correct threshold.
```bash
vim resource_filter
```
3) push changes to git:
```bash
git add resource_filter.py
git commit -m 'adjusting metric threshold'
git push origin HEAD:<branch_name>
```
4) Login into salt master and pull changes to controll nodes, it is presumed that at `usr/lib/python2.7/dist-packages/stc_nova_filters` correct branch is already checkout out, and only pull is required:
```bash
salt ctl* cmd.run 'cd /usr/lib/python2.7/dist-packages/stc_nova_filters && git pull'
```
5) Restart nova-schedulers one by one:
```bash
salt ctl01* service.restart nova-scheduler
```

### If u need to modify, prometheus timeout, use the same procedure as with thresholds, keep in mind correct branch names.

# NOTE: If you have any issues with scheduler, kkalynovskyi@mirantis.com, or find me in slack.