#!/usr/bin/python
from string import Template

RELEASE_STELLA_CONFIG_TPL = \
'RELEASE_NOTE_PROJECT_NAME="HP %s 64bit"\n\
RELEASE_NOTE_CONFIG_NAME="base-config-%s"\n\
RELEASE_NOTE_CONTACTS_NAME="contacts-%s"\n\
LP_PROJECT="stella"\n\
LP_SERIES="%s"\n\
LP_MILESTONE="%s"\n\
LP_NEXT_MILESTONE="%s"\n\
IBS_ISO="%s"\n\
BATCH_MODE="-b"\n\
RELEASE_ISO_LINK="%s"\n\
RELEASE_ISO_MD5="%s"'

HELP_TPL = \
' == How to use stellabot ==\n\
Speak to her: ex: hi how are u?\n\
\n* [find-ppa] To find the right PPA, right volatile-task and the source * repository: \n\
             /msg stellabot find-ppa 1316983 (oem-balabala-1316983)\n\
             /msg stellabot find-ppa stella-pinglin (oem-balabala-1316983)\n\
\n* [cesg] Find published package and versions:\n\
         /msg stellabot cesg PROJECT_NAME PACKAGE_NAME\n  cesg all PACKAGE_NAME\n\
\n* [auth] Ger authorized:\n\
         /msg stellabot auth PASSWORD\n\
         /msg stellabot auth list\n\
\n* [lp-set] Modify launchpad bug:\n\
           /msg stellabot lp-set bugid=123456 assignee=gerald\n\
\n* [release] Release a milestone (require authendication:\n\
            /msg stellabot release $milestone $next_milestone $isolink\n\
\n* [build] Build on ibs (require authendication:\n\
          /msg stellabot build daan\n\
\n* [copy-proposed] Copy package from -proposed to stella PPA (require * authendication)\n\
                  /msg stellabot copy-proposed $package_name $to_ppa ($series, default: precise)\n\
\n* [sanity] Prepare the form for sanity check (require authendication)\n\
           /msg stellabot sanity $milestone $engineer_id $iso_link\n\
\n* [propagate] Copy package between Stella PPAs (require authendication)\n\
              /msg stellabot propagate copy $ppa_to_copy_pkg_from $ppa_to_copy_pkg_to $package_name\n\
\n* [propagate] Submit requests for live-update (require authendication)\n\
              /msg stellabot propagate staging $ppa_to_propagate $package_name\n\
              /msg stellabot propagate production $ppa_to_propagate\n\
\n* [hps] Return the HPS index of a given bug\n\
        /msg hps $bug1 $bug2 ... $bugN\n\
        /msg hps $launchpad_id\n\
\n* [ask] Ask stellabot questions about project status\n\
          /msg stellabot ask $question\n\
          (question can be: release-today)\n\
\n* [assign] Assign bugs by issue type (require authendication)\n\
            /msg stellabot assign list ($issue_type)\n\
            /msg stellabot assign $issue_type (assign_to=2) $bugid_1 $bugid_2 ...\n\
\n* [ip] Get the ip of the machine bot currently is runnong on\n\
'
DOC_HELP = \
'Usage: doc $type\n\
    The type can be:\n\
        all\n\
        main bootstrap uefi volatile-task amd live-update\n\
        acceptance-test hw-tracking sprint HPS release\n\
        sanity-check stella-tools oem-priority dkms\
'

FINDPPA_OUTPUT = Template('* For $image_base\n\n\
Step 1. Get source:\n\
$$bzr branch lp:~oem-solutions-group/$bzr_source/$package\n\n\
Step 2. Get the source of volatile-task:\n\
$$bzr branch lp:~oem-solutions-group/$bzr_source/$volatiletask\n\n\
Step 3. Make a fix and upload the package to PPA:\n\
$$dput -f ppa:oem-archive/$main_ppa ${package}_$$VERSION_source.changes\n\n\
Step 4. If the fix needs to be uploaded to more than one PPA, make binary copies:\n\
$ppa_copy_section\n\
Step 5. Go to https://oem-ibs.canonical.com/projects/$ibs_section and test the builds.\n ')

FINDPPA_OUTPUT_PPA = Template('$$pes-request-ppa-package-copy --package $package --source $main_ppa --source-series $ubuntu --target $ppa --target-series $ubuntu\n')

