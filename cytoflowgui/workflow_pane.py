#!/usr/bin/env python2.7

# (c) Massachusetts Institute of Technology 2015-2016
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from traits.api import provides, Instance, List
from traitsui.api import View, UI

from pyface.qt import QtGui, QtCore
from pyface.tasks.api import DockPane, IDockPane, Task
from pyface.action.api import ToolBarManager
from pyface.tasks.action.api import TaskAction

from cytoflowgui.workflow import Workflow
from cytoflowgui.op_plugins import IOperationPlugin

@provides(IDockPane)
class WorkflowDockPane(DockPane):
    
    id = 'edu.mit.synbio.workflow_pane'
    name = "Workflow"
    
    # the workflow this pane is displaying
    model = Instance(Workflow)
    
    # the UI object associated with the TraitsUI view
    ui = Instance(UI)
    
    # the application instance from which to get plugin instances
    plugins = List(IOperationPlugin)
    
    # the task serving as the dock pane's controller
    task = Instance(Task)
        
    # an empty, unitialized view
    empty_view = View()
    
    ###########################################################################
    # 'ITaskPane' interface.
    ###########################################################################

    def destroy(self):
        """ 
        Destroy the toolkit-specific control that represents the pane.
        """
        # Destroy the Traits-generated control inside the dock control.
        if self.ui is not None:
            self.ui.dispose()
            self.ui = None
        
        # Destroy the dock control.
        super(WorkflowDockPane, self).destroy()

    ###########################################################################
    # 'IDockPane' interface.
    ###########################################################################


    def create_contents(self, parent):
        """ 
        Create and return the toolkit-specific contents of the dock pane.
        """
 
        self.toolbar = ToolBarManager(orientation='vertical',
                                      show_tool_names = False,
                                      image_size = (32, 32))
                 
        for plugin in self.plugins:
            task_action = TaskAction(name=plugin.short_name,
                                     on_perform = lambda pid=plugin.id: 
                                                    self.task.add_operation(pid),
                                     image = plugin.get_icon())
            self.toolbar.append(task_action)
             
        window = QtGui.QMainWindow()
        window.addToolBar(QtCore.Qt.LeftToolBarArea, 
                          self.toolbar.create_tool_bar(window))
         
        self.ui = self.model.edit_traits(kind='subpanel', parent=window)
        window.setCentralWidget(self.ui.control)
         
        window.setParent(parent)
        parent.setWidget(window)
         
        return window
