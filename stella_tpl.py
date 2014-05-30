#!/usr/bin/python

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
             /msg stellabot find-ppa: find-ppa 1316983 (oem-balabala-1316983)\n\
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
              /msg stellabot propagate $package_name $ppa_to_copy_pkg_from $ppa_to_copy_pkg_to\n\
* [propagate] Submit requests for live-update (require authendication)\n\
              /msg stellabot propagate staging $package_name $ppa_to_propagate\n\
              /msg stellabot propagate production $ppa_to_propagate\n\
'

