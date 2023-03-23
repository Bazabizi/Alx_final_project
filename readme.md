# We will be creating freelancing platform

## Cloning the repo
- `git clone https://github.com/meraf00/fse-project.git`

## Catching up with remote repo
- `git pull`

## When working on your task
1. Catch up with remote
    - `git pull`

2. Branch from `dev` branch
    - `git checkout dev`
    - `git checkout -b your-task-branch`
    
3. Work on the task, edit, create... files on your branch

4. Move back to `dev` branch
    - `git checkout dev`

5. Merge `your-task-branch` with `dev`<br>
<b>Make sure you are in `dev` branch</b>
    - `git merge your-task-branch`

6. Update the remote `dev` branch with your new changes<br>
<b>Make sure you are in `dev` branch</b>
    - `git push -u origin dev`


# Installing python modules and setting up the environment

## You only have to do this once (only the first time you clone the project)
- `pip install virtualenv`
- `virtualenv venv`
- `venv\Scripts\activate`
