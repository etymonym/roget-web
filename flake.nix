{
    description = "A flake for furnishing and initalizing a Roget-Web development environment.";
    
    # System Note:  
    #   The system is hard-coded to `x86_64-linux`
    #   This is because the scripts are written / only tested / known to run on `x86_64-linux`
    #   It may be necessary to make ( large ) modifications to said scripts to use something other than `x86_64-linux`
    #   If your able to get it running on your system feel free to submit a PR!

    inputs = {
        nixpkgs.url = "github:nixos/nixpkgs";
    };

    outputs = { self, nixpkgs, flake-utils }:
        let 
            system = "x86_64-linux";

            pkgs = nixpkgs.legacyPackages.${system};
        in {

            # Executed by `nix develop`
            devShell.${system} = pkgs.mkShell { 

                buildInputs = [ 

                    # PostgreSQL
                    pkgs.postgresql_15

                    # Python 3.11 + Django + Psycopg ( PostgreSQL Bindings )
                    pkgs.python311
                    pkgs.python311Packages.django
                    pkgs.python311Packages.psycopg
                ]; 
            };

            
            packages.${system} = {

                # Executed by `nix run .#init_pg`   
                # Note: Will only work after `nix develop` has been run

                ### Performs 6 steps to initialize PostgreSQL for Roget-Web
                ### 0. Checks whether ./pgsql already exists
                ### 1. Tries to initialize a database cluster at ./pgsql/data
                ### 2. Tries to update ./pgsql/data/postgresql.conf
                ### 3. Tries to start the database server, piping logs to ./pgsql/log
                ### 4. Tries to create RogetWebDB
                ### 5. Tries to shutdown the database server
                
                init_pg = pkgs.writeScriptBin "init_pg" ''

                    # Stores a few frequently referenced directories
                    #wd=$(pwd)
                    db_dir="./pgsql"
                    db_data="$db_dir/data"
                    db_log="$db_dir/log"

                    # 0. Checks that ./pgsql doesn't already exist
                    if [ ! -d $db_dir ]
                    then
                        echo "Database files will be stored at '$db_dir'"
                    else
                        if [ -d $db_data ]
                        then
                            echo "'$db_data' already exists!"
                            echo "Make sure you haven't already initialized a local database cluster."
                            exit "1"
                        else
                            echo "'$db_dir' already exists!"
                            while [ true ]
                            do
                                read -p "Pollute '$db_dir' with database cluster? [Y]es or [N]o: " choice
                                lower_choice=$(echo "$choice" | awk '{print tolower($0)}' )
                                if [ $lower_choice == "y" ] || [ $lower_choice == "yes" ]
                                then
                                    echo "Polluting '$db_dir'..."
                                    break
                                elif [ $lower_choice == "n" ] || [ $lower_choice == "no" ]
                                then
                                    echo "Can not initialize database cluster!"
                                    exit "1"
                                else
                                    echo "Please answer [Y]es or [N]o."
                                fi
                            done
                        fi
                    fi

                    # 1. Tries to initialize a database cluster at db_data
                    if pg_ctl -D $db_data -o "-E 'UTF-8'" initdb 
                    then 
                        echo "Database cluster succesfully initialized at '$db_data'"
                    else
                        echo "Failed to initialize database cluster at '$db_data'!"
                        exit "1"
                    fi

                    # Create the necessary `sed` arguments 
                    # Used to update where PostgreSQL will listen for connections
                    find="#unix_socket_directories = '/run/postgresql'	# comma-separated list of directories"
                    replace="unix_socket_directories = \'../\'	# set to listen at ../"

                    # 2. Tries to update postgresql.conf ( found in db_data )
                    if sed -i "s:$find:$replace:" $db_data/postgresql.conf && 
                    [ $(grep -c "unix_socket_directories = '../'	# set to listen at ../" $db_data/postgresql.conf) == "1" ]
                    then
                        echo "Database sockets configured succesfully!"
                    else
                        echo "Failed to configure 'unix_socket_directories' in '$db_data/postgresql.conf'!"
                        exit "1"
                    fi

                    # 3. Tries to start the database server, piping logs to db_log
                    if pg_ctl -D $db_data -l $db_log  start
                    then
                        echo "Database server succesfully started!"
                    else
                        echo "Failed to start Database Server!"
                        exit "1"
                    fi

                    # 4. Tries to create RogetWebDB
                    if createdb RogetWebDB -h "$(pwd)/pgsql"
                    then
                        echo "RogetWebDB succesfully created!"
                    else
                        echo "Failed to create RogetWebDB!"
                        exit "1"
                    fi

                    # 5. Tries to shutdown the database server
                    if [ ! 'pg_ctl: no server running' = "$(pg_ctl -D $db_data status)" ]
                    then 
                        if pg_ctl -D $db_data stop
                        then
                            echo "Database server has been succesfully shutdown."
                        else
                            echo "Failed to shutdown Database server!"
                            echo "Important: Do not delete '$db_dir/.s.PGSQL_5432' or '$db_dir/.s.PGSQL_5432.lock' manually!"
                            echo "If a full-wipe is needed, try 'nix run .#wipe_pg'"
                        fi
                    else
                        echo "No server running?"
                        exit "1"
                    fi
                    echo "PostgreSQL initialization for local Roget-Web instance succesfully completed!"
                '';

                # Executed by `nix run .#start_pg`
                # Note: Will only work after `nix run .#init_pg` has been run

                # Tries to start the PostgreSQL server
                start_pg = pkgs.writeScriptBin "start_pg" ''

                    # Tries to start the database server, piping logs to './pgsql/log'
                    if pg_ctl -D ./pgsql/data -l ./pgsql/log  start
                    then
                        echo "Database server succesfully started!"
                    else
                        echo "Failed to start Database Server!"
                        exit "1"
                    fi
                '';

                # Executed by `nix run .#stop_pg`
                # Note: Will only work after `nix run .#init_pg` has been run

                # Tries to shutdown the database server
                stop_pg = pkgs.writeScriptBin "stop_pg" ''

                    wd=$(pwd)

                    if [ ! 'pg_ctl: no server running' = "$(pg_ctl -D ./pgsql/data status)" ]
                    then 
                        if pg_ctl -D ./pgsql/data stop
                        then
                            echo "Database server has been succesfully shutdown."
                        else
                            echo "Failed to shutdown Database server!"
                            echo "Important: Do not delete '$wd/pgsql/.s.PGSQL_5432' or '$wd/pgsql/.s.PGSQL_5432.lock' manually!"
                            echo "If a full-wipe is needed, try 'nix run .#wipe_pg'"
                        fi
                    else
                        echo "Can not find database server if one is running."
                        exit "1"
                    fi
                '';



                # Executed by `nix run .#wipe_pg`   
                # Note: Will only work after `nix develop` has been run

                ### Performs 4 steps to wipe local PostgreSQL instance
                ### 1. Checks if there is a database cluster at ./pgsql/data
                ### 2. Tries to update `unix_socket_directories` in ./pgsql/data/postgresql.conf
                ### 3. Tries to start the database server, piping logs to ./pgsql/log
                ### 4. Tries to create RogetWebDB
                ### 5. Tries to shutdown the database server

                wipe_pg = pkgs.writeScriptBin "wipe_pg" ''

                    # Stores a few frequently referenced directories
                    #wd=$(pwd)
                    db_dir="./pgsql"
                    db_data="$db_dir/data"
                    db_log="$db_dir/log"

                    if [ -d $db_data ]
                    then
                        echo "Local database cluster found at '$db_data'"
                    else
                        echo "No database cluster found; nothing to do."
                        exit "1"
                    fi

                    if [ !'pg_ctl: no server running' = "$(pg_ctl -D ./pgsql/data status)" ]
                    then 
                        pg_ctl -D ./pgsql/data/ stop
                        echo "Database server has been shutdown... OK"
                    else
                        echo "No database server running... OK"
                    fi

                    if mv ./pgsql/log ./pgsql_log
                    then
                        echo "Log moved to '$wd/pgsql_log' "
                    else
                        echo "No log found... OK"
                    fi

                    if rm -r ./pgsql
                    then
                        echo "Database cluster has been deleted... OK"
                    else 
                        echo "Failed to delete database files... Err"
                        exit "1"
                    fi
                    echo "Local PostgreSQL wipe completed."
                '';
            };
        };
}